import json
import re

from sqlalchemy.orm import Session

from ..models import Paper, ScreeningResult
from .ollama_service import AI_MODEL_ID, generate_text

SCREENING_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "population_match": {"type": "boolean"},
        "intervention_match": {"type": "boolean"},
        "comparison_match": {"type": "boolean"},
        "outcome_match": {"type": "boolean"},
        "study_type_match": {"type": "boolean"},
        "decision": {
            "type": "string",
            "enum": ["Include", "Exclude", "Uncertain"],
        },
        "confidence": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        },
        "reason": {"type": "string", "minLength": 1},
    },
    "required": [
        "population_match",
        "intervention_match",
        "comparison_match",
        "outcome_match",
        "study_type_match",
        "decision",
        "confidence",
        "reason",
    ],
    "additionalProperties": False,
}


# ============================================================
# HELPERS
# ============================================================

def _safe_json_parse(text: str) -> dict:
    """
    Safely parse JSON returned by Ollama.
    """

    if not text:
        raise ValueError(
            "Ollama returned an empty response."
        )

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    try:
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError(
                "Ollama Model 2 must return a JSON object."
            )
        return parsed

    except json.JSONDecodeError:

        # Try to find JSON object inside response
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:

            json_text = text[
                start:end + 1
            ]

            try:

                parsed = json.loads(json_text)
                if not isinstance(parsed, dict):
                    raise ValueError(
                        "Ollama Model 2 must return a JSON object."
                    )
                return parsed

            except json.JSONDecodeError:
                pass

        raise ValueError(
            "Ollama returned invalid JSON."
        )


def _normalize_decision(decision: str) -> str:

    if not isinstance(decision, str) or not decision.strip():
        raise ValueError(
            "Ollama Model 2 did not return a screening decision."
        )

    decision = decision.strip().lower()

    if decision == "include":
        return "Include"

    if decision == "exclude":
        return "Exclude"

    if decision == "uncertain":
        return "Uncertain"

    raise ValueError(
        f"Ollama Model 2 returned an invalid decision: {decision!r}."
    )


def _normalize_match(value) -> bool:

    if isinstance(value, bool):
        return value

    if isinstance(value, str):

        normalized = value.strip().lower()
        if normalized in {
            "true",
            "yes",
            "match",
            "matched",
            "1"
        }:
            return True
        if normalized in {
            "false",
            "no",
            "no match",
            "unmatched",
            "0",
        }:
            return False

    if isinstance(value, int):

        if value in (0, 1):
            return value == 1

    raise ValueError(
        "Ollama Model 2 returned an invalid PICOS match value."
    )


# ============================================================
# MODEL 2 — SINGLE PAPER
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
    full_text: str | None = None,
    full_text_available: bool = False,
):
    """
    Screen one paper using Ollama Model 2.
    """

    if not title:
        raise ValueError(
            "Paper title is required."
        )

    has_full_text = bool(full_text and full_text.strip())

    # Truncate full text to prevent timeouts on large documents
    max_content_chars = 4000
    if has_full_text:
        paper_content = full_text.strip()[:max_content_chars]
    else:
        paper_content = (abstract or "Not available.")[:max_content_chars]

    content_label = "Full text" if has_full_text else "Abstract"

    prompt = f"""
You are an expert systematic literature review screening assistant.

Your task is to screen ONE research paper using PICOS criteria.

Return ONLY valid JSON.
Do not return markdown.
Do not return explanations outside JSON.

==================================================
PAPER
==================================================

Title:
{title}

{content_label}:
{paper_content}

Full text attached to this project:
{"Yes" if full_text_available else "No"}

==================================================
PICOS CRITERIA
==================================================

Population:
{population or "Not specified"}

Intervention:
{intervention or "Not specified"}

Comparison:
{comparison or "Not specified"}

Outcome:
{outcome or "Not specified"}

Study Type:
{study_type or "Not specified"}

Restriction:
{restriction or "No restriction"}

Research Limitations / Requirements:
{limitations or "None specified"}

Apply both items above as eligibility criteria. Exclude a paper only when the
supplied evidence clearly violates a criterion; use Uncertain when evidence is
insufficient. If the restriction requires full text, it is satisfied only
when full text is attached to this project and included in the supplied text;
a DOI or external link alone is not full-text access.

==================================================
SCREENING RULES
==================================================

Evaluate the paper carefully.

Determine:

1. Does the population match?
2. Does the intervention match?
3. Does the comparison match?
4. Does the outcome match?
5. Does the study type match?
6. Does the paper satisfy the restriction?
7. Does the paper satisfy the stated limitations/requirements?

Decision rules:

Include:
The paper is sufficiently relevant to the research question.

Exclude:
The paper is clearly irrelevant or fails important eligibility criteria.

Uncertain:
The supplied paper text does not contain enough information to make a reliable decision.

Use the full text when provided; otherwise use the abstract.
Do not invent information that is not present in the supplied paper text.

==================================================
OUTPUT FORMAT
==================================================

{{
    "population_match": true,
    "intervention_match": true,
    "comparison_match": true,
    "outcome_match": true,
    "study_type_match": true,
    "decision": "Include",
    "confidence": 85,
    "reason": "Short evidence-based explanation."
}}
"""

    # Retry once on invalid JSON
    for attempt in range(2):
        response_text = generate_text(
            prompt,
            format=SCREENING_RESPONSE_SCHEMA,
            max_output_tokens=256,
        )

        try:
            result = _safe_json_parse(response_text)
            break
        except (json.JSONDecodeError, ValueError) as error:
            if attempt == 1:
                raise ValueError(
                    "Ollama Model 2 returned an invalid screening response "
                    f"after one retry: {error}"
                ) from error
            print(
                "Ollama Model 2 returned an invalid response; retrying once."
            )

    decision = _normalize_decision(
        result.get("decision")
    )

    try:
        raw_confidence = result["confidence"]
        if isinstance(raw_confidence, bool):
            raise TypeError("Boolean is not a confidence score.")
        if isinstance(raw_confidence, float) and not raw_confidence.is_integer():
            raise ValueError("Confidence must be an integer.")
        confidence = int(raw_confidence)

    except (KeyError, TypeError, ValueError) as error:

        raise ValueError(
            "Ollama Model 2 must return integer confidence."
        ) from error

    if not 0 <= confidence <= 100:
        raise ValueError(
            "Ollama Model 2 confidence must be between 0 and 100."
        )

    reason = result.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError(
            "Ollama Model 2 must return an evidence-based reason."
        )

    return {

        "population_match":
            _normalize_match(
                result.get(
                    "population_match"
                )
            ),

        "intervention_match":
            _normalize_match(
                result.get(
                    "intervention_match"
                )
            ),

        "comparison_match":
            _normalize_match(
                result.get(
                    "comparison_match"
                )
            ),

        "outcome_match":
            _normalize_match(
                result.get(
                    "outcome_match"
                )
            ),

        "study_type_match":
            _normalize_match(
                result.get(
                    "study_type_match"
                )
            ),

        "decision":
            decision,

        "confidence":
            confidence,

        "reason": reason.strip()
    }


# ============================================================
# MODEL 2 — PROJECT PAPERS (SEQUENTIAL — NO PARALLEL)
# ============================================================

def screen_project_papers(
    db: Session,
    project_id: int,
    population: str,
    intervention: str,
    comparison: str,
    outcome: str,
    study_type: str,
    paper_ids=None,
    restriction: str | None = None,
    limitations: str | None = None
):
    """
    Screen papers belonging to a specific project.

    Papers are processed SEQUENTIALLY to avoid overwhelming Ollama
    (a single-model inference server). Existing screening results
    are reused (cached) to avoid redundant AI calls.

    IMPORTANT:
    ScreeningResult does not use project_id.
    Project ownership is verified through Paper.project_id.
    """

    # --------------------------------------------------------
    # Get project papers
    # --------------------------------------------------------

    query = db.query(Paper).filter(
        Paper.project_id == project_id
    )

    if paper_ids:

        query = query.filter(
            Paper.id.in_(paper_ids)
        )

    papers = query.order_by(
        Paper.id
    ).all()

    if not papers:

        raise ValueError(
            "No papers found for this project."
        )

    print()
    print("=" * 70)
    print("MODEL 2 PROJECT SCREENING (SEQUENTIAL)")
    print("=" * 70)

    print(
        f"Project ID: {project_id}"
    )

    print(
        f"Papers to screen: {len(papers)}"
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    results = []

    ai_calls = 0
    cached_results = 0

    total_papers = len(papers)

    for index, paper in enumerate(papers, start=1):

        print(
            f"\nModel 2 screening "
            f"{index}/{total_papers}: "
            f"{paper.title[:80]}"
        )

        # ----------------------------------------------------
        # Check existing result (cache)
        # ----------------------------------------------------

        existing_result = (
            db.query(ScreeningResult)
            .filter(
                ScreeningResult.paper_id == paper.id
            )
            .first()
        )

        if existing_result:

            print(
                "Using cached Model 2 result."
            )

            cached_results += 1

            results.append({
                "paper_id": paper.id,
                "title": paper.title,
                "publication_year": paper.publication_year,
                "source": paper.source,
                "doi": paper.doi,
                "url": paper.url,
                "full_text_used": bool(
                    paper.full_text and paper.full_text.strip()
                ),
                "full_text_available": bool(
                    paper.full_text and paper.full_text.strip()
                ),
                "population_match": True,
                "intervention_match": True,
                "comparison_match": True,
                "outcome_match": True,
                "study_type_match": True,
                "decision": existing_result.decision,
                "confidence": existing_result.confidence_score,
                "reason": existing_result.reason,
                "ai_model": AI_MODEL_ID,
                "cached": True,
            })

            continue

        # ----------------------------------------------------
        # Run Model 2 screening (SEQUENTIAL, one at a time)
        # ----------------------------------------------------

        print("Running Ollama Model 2...")

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
                full_text=paper.full_text,
                full_text_available=bool(
                    paper.full_text and paper.full_text.strip()
                ),
            )
        except Exception as error:
            print(f"Model 2 screening failed for paper {paper.id}: {error}")
            # On failure, mark as Uncertain so the pipeline can continue
            result = {
                "population_match": False,
                "intervention_match": False,
                "comparison_match": False,
                "outcome_match": False,
                "study_type_match": False,
                "decision": "Uncertain",
                "confidence": 0,
                "reason": f"AI screening failed: {str(error)[:200]}",
            }

        ai_calls += 1

        # ----------------------------------------------------
        # Save ScreeningResult
        #
        # DO NOT use project_id here.
        # ScreeningResult belongs to Paper.
        # ----------------------------------------------------

        screening_record = ScreeningResult(

            paper_id=paper.id,
            decision=
                result[
                    "decision"
                ],

            confidence_score=str(result["confidence"]),

            reason=
                result[
                    "reason"
                ],

            ai_model=
                AI_MODEL_ID
        )

        db.add(
            screening_record
        )

        # Commit after each paper to avoid losing progress
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        final_result = {

            "paper_id":
                paper.id,

            "title":
                paper.title,

            "publication_year":
                paper.publication_year,

            "source":
                paper.source,

            "doi":
                paper.doi,

            "url":
                paper.url,

            "full_text_used":
                bool(paper.full_text and paper.full_text.strip()),

            "full_text_available":
                bool(paper.full_text and paper.full_text.strip()),

            "population_match":
                result[
                    "population_match"
                ],

            "intervention_match":
                result[
                    "intervention_match"
                ],

            "comparison_match":
                result[
                    "comparison_match"
                ],

            "outcome_match":
                result[
                    "outcome_match"
                ],

            "study_type_match":
                result[
                    "study_type_match"
                ],

            "decision":
                result[
                    "decision"
                ],

            "confidence":
                result[
                    "confidence"
                ],

            "reason":
                result[
                    "reason"
                ],

            "ai_model":
                AI_MODEL_ID
        }

        results.append(
            final_result
        )

        print(
            f"Decision: "
            f"{result['decision']}"
        )

        print(
            f"Confidence: "
            f"{result['confidence']}"
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    included = [
        result
        for result in results
        if result["decision"]
        == "Include"
    ]

    uncertain = [
        result
        for result in results
        if result["decision"]
        == "Uncertain"
    ]

    excluded = [
        result
        for result in results
        if result["decision"]
        == "Exclude"
    ]

    print()
    print("=" * 70)
    print("MODEL 2 COMPLETED")
    print("=" * 70)

    print(
        f"Total screened: {len(results)}"
    )

    print(
        f"Included: {len(included)}"
    )

    print(
        f"Uncertain: {len(uncertain)}"
    )

    print(
        f"Excluded: {len(excluded)}"
    )

    print(
        f"Ollama calls: {ai_calls}"
    )

    print(
        f"Cached results: {cached_results}"
    )

    return {

        "total_screened":
            len(results),

        "ai_calls":
            ai_calls,

        "cached_results":
            cached_results,

        "results":
            results,

        "included":
            included,

        "uncertain":
            uncertain,

        "excluded":
            excluded,

        "included_count":
            len(included),

        "uncertain_count":
            len(uncertain),

        "excluded_count":
            len(excluded),

        "shortlist":
            included + uncertain,

        "shortlist_count":
            len(included) + len(uncertain)
    }