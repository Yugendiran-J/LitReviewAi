import json

from ..models import Paper, ScreeningResult
from ..services.ollama_service import AI_MODEL_ID, generate_text


def _parse_screening_response(response_text: str) -> dict:
    data = json.loads(response_text)
    if not isinstance(data, dict):
        raise ValueError("Ollama Model 2 must return a JSON object.")

    decision = data.get("decision")
    if decision not in {"Include", "Exclude", "Uncertain"}:
        raise ValueError(f"Invalid screening decision: {decision}")

    confidence = data.get("confidence")
    if isinstance(confidence, bool):
        raise ValueError("Ollama Model 2 returned invalid confidence.")
    try:
        confidence = float(confidence)
    except (ValueError, TypeError) as error:
        raise ValueError("Ollama Model 2 returned invalid confidence.") from error
    if not 0 <= confidence <= 100:
        raise ValueError("Ollama Model 2 returned invalid confidence.")
    data["confidence"] = confidence

    reason = data.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Ollama Model 2 must return a screening reason.")
    data["reason"] = reason.strip()

    picos_analysis = data.get("picos_analysis")
    required_picos = {
        "population",
        "intervention",
        "comparison",
        "outcome",
        "study_type",
    }
    valid_picos_values = {"Match", "Partial", "No match", "Not reported"}
    if (
        not isinstance(picos_analysis, dict)
        or set(picos_analysis) != required_picos
        or any(
            not isinstance(value, str) or value not in valid_picos_values
            for value in picos_analysis.values()
        )
    ):
        raise ValueError("Ollama Model 2 returned invalid PICOS analysis.")

    return data


# ============================================================
# AI MODEL 2 — DEEP PICOS SCREENING
# ============================================================

def screen_candidate_paper(
    title: str,
    abstract: str,
    population: str,
    intervention: str,
    comparison: str,
    outcome: str,
    study_type: str,
    restriction: str | None = None,
    limitations: str | None = None,
):
    """
    Screen one research paper using PICOS criteria.

    Returns:
        decision
        confidence
        reason
        picos_analysis
    """

    # Truncate abstract to prevent timeouts on very large texts
    max_content_chars = 4000
    abstract_text = (abstract or "Abstract not available.")[:max_content_chars]

    prompt = f"""
Screen this paper against the research eligibility criteria using only its
title and abstract. Do not infer missing evidence. Mark each PICOS item as
"Match", "Partial", "No match", or "Not reported". Exclude only for a clear
eligibility mismatch; use "Uncertain" when evidence is insufficient. Apply the
restriction and limitations. Give a brief evidence-based reason and confidence
from 0 to 100. Keep the reason to one sentence of at most 25 words. Return only
JSON in this exact shape:
{{
  "decision": "Include",
  "confidence": 85,
  "reason": "Brief evidence-based reason.",
  "picos_analysis": {{
    "population": "Match",
    "intervention": "Match",
    "comparison": "Partial",
    "outcome": "Match",
    "study_type": "Match"
  }}
}}

Criteria:
Population: {population or "Not specified"}
Intervention: {intervention or "Not specified"}
Comparison: {comparison or "Not specified"}
Outcome: {outcome or "Not specified"}
Study type: {study_type or "Not specified"}
Restriction: {restriction or "No restriction"}
Limitations: {limitations or "None specified"}

Paper title: {title}
Paper abstract: {abstract_text}
"""

    # ========================================================
    # CALL OLLAMA MODEL
    # ========================================================

    for attempt in range(2):
        response_text = generate_text(
            prompt,
            format="json",
            max_output_tokens=256,
        )
        try:
            data = _parse_screening_response(response_text)
            break
        except (json.JSONDecodeError, ValueError) as error:
            if attempt == 1:
                raise ValueError(
                    "Ollama Model 2 returned an invalid screening response "
                    f"after one retry: {error}"
                ) from error
            print(
                "Ollama Model 2 returned an invalid screening response; "
                "retrying once."
            )

    return data


# ============================================================
# AI MODEL 2 — SCREEN ALL PROJECT PAPERS (SEQUENTIAL)
# ============================================================
def screen_project_papers(
    db,
    project_id,
    population,
    intervention,
    comparison,
    outcome,
    study_type,
    paper_ids=None,
    restriction: str | None = None,
    limitations: str | None = None,
):
    """
    Model 2 PICOS screening.

    IMPORTANT:
    Model 2 is allowed to process ONLY the paper IDs
    explicitly supplied through paper_ids.

    Papers are screened SEQUENTIALLY (one at a time) to avoid
    overloading Ollama.

    A hard maximum of 20 papers is enforced.
    """

    MAX_MODEL2_PAPERS = 20

    # =========================================================
    # SAFETY CHECK
    # =========================================================

    if not paper_ids:
        raise ValueError(
            "No paper IDs were provided to Model 2. "
            "Refusing to screen all project papers."
        )

    # Remove duplicates while preserving order
    paper_ids = list(
        dict.fromkeys(paper_ids)
    )

    # HARD LIMIT
    paper_ids = paper_ids[
        :MAX_MODEL2_PAPERS
    ]

    print("\n" + "=" * 70)
    print("MODEL 2 SAFETY CHECK")
    print("=" * 70)

    print(
        f"Paper IDs received: "
        f"{len(paper_ids)}"
    )

    print(
        f"Maximum allowed: "
        f"{MAX_MODEL2_PAPERS}"
    )

    # =========================================================
    # QUERY ONLY SELECTED PAPERS
    # =========================================================

    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id,
            Paper.id.in_(paper_ids)
        )
        .all()
    )

    # Preserve the order supplied by pipeline
    paper_map = {
        paper.id: paper
        for paper in papers
    }

    ordered_papers = [
        paper_map[paper_id]
        for paper_id in paper_ids
        if paper_id in paper_map
    ]

    if not ordered_papers:
        raise ValueError(
            "None of the supplied paper IDs "
            "belong to this project."
        )

    print(
        f"Actual papers loaded for Model 2: "
        f"{len(ordered_papers)}"
    )

    # =========================================================
    # PROCESS PAPERS SEQUENTIALLY
    # =========================================================

    results_by_id = {}

    ai_calls = 0
    cached_results = 0

    total_papers = len(
        ordered_papers
    )

    for index, paper in enumerate(
        ordered_papers,
        start=1
    ):

        print(
            f"\nModel 2 screening "
            f"{index}/{total_papers}: "
            f"{paper.title[:80]}"
        )

        # -----------------------------------------------------
        # Check existing result
        # -----------------------------------------------------

        existing_result = (
            db.query(ScreeningResult)
            .filter(
                ScreeningResult.paper_id == paper.id
            )
            .first()
        )

        # -----------------------------------------------------
        # Use cached result
        # -----------------------------------------------------

        if existing_result:

            print(
                "Using cached Model 2 result."
            )

            cached_results += 1

            results_by_id[paper.id] = {
                "paper_id": paper.id,
                "title": paper.title,
                "publication_year": paper.publication_year,
                "source": paper.source,
                "doi": paper.doi,
                "url": paper.url,
                "decision": existing_result.decision,
                "confidence": existing_result.confidence_score,
                "reason": existing_result.reason,
                "picos_analysis": {},
                "full_text_used": False,
                "cached": True,
            }

            continue

        # -----------------------------------------------------
        # Run AI screening
        # -----------------------------------------------------

        try:
            result = screen_candidate_paper(
                title=paper.title,
                abstract=paper.abstract or "",
                population=population or "",
                intervention=intervention or "",
                comparison=comparison or "",
                outcome=outcome or "",
                study_type=study_type or "",
                restriction=restriction,
                limitations=limitations,
            )
        except Exception as error:
            print(f"Model 2 screening failed for paper {paper.id}: {error}")
            result = {
                "decision": "Uncertain",
                "confidence": 0,
                "reason": f"AI screening failed: {str(error)[:200]}",
                "picos_analysis": {},
            }

        ai_calls += 1
        screening_record = ScreeningResult(
            paper_id=paper.id,
            decision=result["decision"],
            confidence_score=str(result["confidence"]),
            reason=result["reason"],
            ai_model=AI_MODEL_ID,
        )
        db.add(screening_record)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        results_by_id[paper.id] = {
            "paper_id": paper.id,
            "title": paper.title,
            "publication_year": paper.publication_year,
            "source": paper.source,
            "doi": paper.doi,
            "url": paper.url,
            "decision": result["decision"],
            "confidence": result["confidence"],
            "reason": result["reason"],
            "picos_analysis": result.get("picos_analysis", {}),
            "full_text_used": False,
            "ai_model": AI_MODEL_ID,
            "cached": False,
        }

    results = [
        results_by_id[paper.id]
        for paper in ordered_papers
        if paper.id in results_by_id
    ]

    # =========================================================
    # SUMMARY
    # =========================================================

    print("\n" + "=" * 70)
    print("MODEL 2 SUMMARY")
    print("=" * 70)

    print(
        f"Total papers processed: "
        f"{len(ordered_papers)}"
    )

    print(
        f"Ollama calls: "
        f"{ai_calls}"
    )

    print(
        f"Cached results: "
        f"{cached_results}"
    )

    return results