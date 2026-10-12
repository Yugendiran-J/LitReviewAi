from sqlalchemy.orm import Session

from ..ai.pipeline_service import run_literature_pipeline

from ..services.fulltext_shortlist_service import (
    get_fulltext_candidates
)

from ..services.model3_processing_service import (
    process_model3_extraction
)

from ..services.model3_verification_service import (
    process_model3_verification
)

from ..models import Paper


def run_end_to_end_pipeline(
    db: Session,
    project_id: int,
    keyword: str,
    domain: str | None,
    population: str | None,
    intervention: str | None,
    comparison: str | None,
    outcome: str | None,
    study_type: str | None,
    year_from: int | None = None,
    year_to: int | None = None,
    restriction: str | None = None,
    limitations: str | None = None,
    sources: list[str] | None = None,
):

    print()
    print("=" * 70)
    print("STARTING END-TO-END LITERATURE REVIEW PIPELINE")
    print("=" * 70)

    # =========================================================
    # MODEL 1 + MODEL 2
    # =========================================================

    discovery_screening_result = run_literature_pipeline(
        db=db,
        project_id=project_id,
        research_topic=keyword,
        research_question=domain,
        population=population,
        intervention=intervention,
        comparison=comparison,
        outcome=outcome,
        study_type=study_type,
        year_from=year_from,
        year_to=year_to,
        restriction=restriction,
        limitations=limitations,
        sources=sources,
    )

    # =========================================================
    # FULL TEXT SHORTLIST
    # =========================================================

    model2_results_raw = discovery_screening_result.get(
        "model2", {}
    ).get("results", [])

    candidate_paper_ids = []
    for item in model2_results_raw:
        if isinstance(item, dict):
            pid = item.get("paper_id") or item.get("id")
            if pid:
                candidate_paper_ids.append(pid)
        elif isinstance(item, int):
            candidate_paper_ids.append(item)

    fulltext_candidates = get_fulltext_candidates(
        db=db,
        project_id=project_id,
        paper_ids=candidate_paper_ids,
    )

    shortlist_papers = (
        fulltext_candidates.get("included", [])
        + fulltext_candidates.get("uncertain", [])
    )

    print()
    print("=" * 70)
    print("FULL-TEXT SHORTLIST")
    print("=" * 70)

    print(
        f"Candidates: {len(shortlist_papers)}"
    )

    extraction_results = []
    verification_results = []
    model3_errors = []
    model3_skipped = []
    preparation = discovery_screening_result.get(
        "fulltext_preparation", {}
    )

    preparation_errors = {}
    for item in preparation.get("errors", []):
        if isinstance(item, dict):
            pid = item.get("paper_id") or item.get("id")
            if pid:
                preparation_errors[pid] = item.get("error", "Full text error")
        elif isinstance(item, str):
            preparation_errors["unknown"] = item

    # =========================================================
    # MODEL 3
    # =========================================================

    for index, paper_data in enumerate(
        shortlist_papers,
        start=1
    ):
        if isinstance(paper_data, dict):
            paper_id = paper_data.get("paper_id") or paper_data.get("id")
        elif isinstance(paper_data, int):
            paper_id = paper_data
        else:
            paper_id = None

        print()
        print("-" * 70)
        print(
            f"MODEL 3 PAPER "
            f"{index}/{len(shortlist_papers)}"
        )
        print("-" * 70)

        if not paper_id:
            print("Skipping: paper_id missing.")
            continue

        paper = db.query(Paper).filter(
            Paper.id == paper_id,
            Paper.project_id == project_id
        ).first()

        if not paper:
            print(
                f"Paper {paper_id} not found."
            )
            continue

        print(
            f"Title: {paper.title}"
        )

        if paper.id in preparation_errors:
            model3_errors.append({
                "paper_id": paper.id,
                "title": paper.title,
                "stage": "full_text_processing",
                "error": preparation_errors[paper.id],
            })
            continue

        if not paper.pdf_path and not paper.full_text:
            print(
                "Full text is not available."
            )
            model3_skipped.append({
                "paper_id": paper.id,
                "title": paper.title,
                "reason": "Attach a full-text PDF to enable evidence extraction.",
            })
            continue

        # -----------------------------------------------------
        # EXTRACTION
        # -----------------------------------------------------

        try:

            extraction_result = (
                process_model3_extraction(
                    db=db,
                    paper_id=paper.id,
                    project_id=project_id
                )
            )

            extraction_results.append(
                extraction_result
            )

            print(
                "Extraction completed."
            )

        except Exception as error:

            print(
                "Model 3 extraction failed:"
            )

            print(error)

            model3_errors.append({
                "paper_id": paper.id,
                "title": paper.title,
                "stage": "extraction",
                "error": str(error),
            })
            continue

        # -----------------------------------------------------
        # VERIFICATION
        # -----------------------------------------------------

        extraction_data = {}

        if isinstance(
            extraction_result,
            dict
        ):

            extraction_data = (
                extraction_result.get(
                    "extraction",
                    {}
                )
            )

        if not isinstance(
            extraction_data,
            dict
        ):

            extraction_data = {}

        claim = extraction_data.get(
            "conclusion",
            ""
        )

        if (
            not claim
            or claim == "Not reported"
        ):

            print(
                "No conclusion available "
                "for verification."
            )

            model3_skipped.append({
                "paper_id": paper.id,
                "title": paper.title,
                "reason": "Model 3 extraction returned no conclusion to verify.",
            })
            continue

        try:

            verification_result = (
                process_model3_verification(
                    db=db,
                    paper_id=paper.id,
                    project_id=project_id,
                    claim=claim
                )
            )

            verification_results.append(
                verification_result
            )

            print(
                "Evidence verification completed."
            )

        except Exception as error:

            print(
                "Evidence verification failed:"
            )

            print(error)

            model3_errors.append({
                "paper_id": paper.id,
                "title": paper.title,
                "stage": "verification",
                "error": str(error),
            })

    # =========================================================
    # FINAL RESULT
    # =========================================================

    included = discovery_screening_result.get(
        "included",
        []
    )

    uncertain = discovery_screening_result.get(
        "uncertain",
        []
    )

    excluded = discovery_screening_result.get(
        "excluded",
        []
    )

    return {
        "project_id": project_id,

        "filters": {
            "year_from": year_from,
            "year_to": year_to,
            "restriction": restriction,
            "limitations": limitations,
            "sources": sources or ["pubmed"],
        },

        "discovery_screening": {
            **discovery_screening_result,
            "included": included,
            "uncertain": uncertain,
            "excluded": excluded
        },

        "fulltext_candidates": fulltext_candidates,

        "model3": {
            "extraction_results": extraction_results,
            "verification_results": verification_results,
            "extraction_count": len(
                extraction_results
            ),
            "verification_count": len(
                verification_results
            ),
            "errors": model3_errors,
            "skipped": model3_skipped,
        }
    }