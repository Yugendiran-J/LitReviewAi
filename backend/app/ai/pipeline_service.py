from ..services.discovery_service import generate_search_queries
from ..services.ollama_service import OllamaTimeoutError

from .candidate_service import (
    collect_candidate_papers,
    save_candidate_papers,
    update_candidate_abstracts
)

from .prefilter_service import prefilter_papers

from .screening_model2_service import (
    screen_project_papers
)


def run_literature_pipeline(
    db,
    project_id: int,
    research_topic: str,
    research_question: str | None = None,
    population: str | None = None,
    intervention: str | None = None,
    comparison: str | None = None,
    outcome: str | None = None,
    study_type: str | None = None,
    keywords: list[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    restriction: str | None = None,
    limitations: str | None = None,
    sources: list[str] | None = None,
):

    print()
    print("=" * 70)
    print("STARTING LITERATURE REVIEW PIPELINE")
    print("=" * 70)

    # =========================================================
    # MODEL 1
    # =========================================================

    print()
    print("=" * 70)
    print("STEP 1: AI MODEL 1 - DISCOVERY")
    print("=" * 70)

    try:
        discovery_result = generate_search_queries(
            research_topic=research_topic,
            research_question=research_question,
            population=population,
            intervention=intervention,
            comparison=comparison,
            outcome=outcome,
            study_type=study_type,
            sources=sources,
        )
    except Exception as error:
        if isinstance(error, OllamaTimeoutError):
            raise
        raise RuntimeError(f"AI Discovery failed: {error}") from error

    queries = discovery_result["queries"]

    # =========================================================
    # CANDIDATES
    # =========================================================

    print()
    print("=" * 70)
    print("STEP 2: CANDIDATE PAPER COLLECTION")
    print("=" * 70)

    try:
        candidate_result = collect_candidate_papers(
            queries=queries,
            max_results_per_query=10,
            sources=sources,
        )
    except Exception as error:
        raise RuntimeError(f"Candidate Collection failed: {error}") from error

    candidate_papers = candidate_result["papers"]

    print(
        f"Total candidate papers found: "
        f"{len(candidate_papers)}"
    )

    if not candidate_papers:
        raise ValueError("No candidate papers were found.")

    # =========================================================
    # SAVE
    # =========================================================

    print()
    print("=" * 70)
    print("STEP 3: SAVING CANDIDATE PAPERS")
    print("=" * 70)

    saved_papers = save_candidate_papers(
        db=db,
        project_id=project_id,
        papers=candidate_papers
    )
    candidate_ids = [paper.id for paper in saved_papers]

    print(
        f"Saved/reused papers: {len(saved_papers)}"
    )

    # =========================================================
    # ABSTRACTS
    # =========================================================

    print()
    print("=" * 70)
    print("STEP 4: ABSTRACT RETRIEVAL")
    print("=" * 70)

    abstract_result = update_candidate_abstracts(
        db=db,
        project_id=project_id,
        paper_ids=candidate_ids,
    )

    print(
        f"Abstracts updated: "
        f"{abstract_result.get('updated', 0)}"
    )

    # Reload project papers after abstract retrieval
    from ..models import Paper

    db_papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id,
            Paper.id.in_(candidate_ids),
        )
        .all()
    )

    papers = []

    for paper in db_papers:
        papers.append({
            "id": paper.id,
            "paper_id": paper.id,
            "title": paper.title,
            "abstract": paper.abstract or "",
            "full_text": paper.full_text or "",
            "publication_year": paper.publication_year,
            "authors": paper.authors,
            "journal": paper.journal,
            "doi": paper.doi,
            "url": paper.url,
            "source": paper.source,
        })

    # =========================================================
    # YEAR FILTER
    # =========================================================

    print()
    print("=" * 70)
    print("STEP 5: PUBLICATION YEAR FILTER")
    print("=" * 70)

    year_filtered_papers = papers

    if year_from is not None or year_to is not None:

        year_filtered_papers = []

        for paper in papers:

            publication_year = paper.get(
                "publication_year"
            )

            if not publication_year:
                continue

            if (
                year_from is not None
                and publication_year < year_from
            ):
                continue

            if (
                year_to is not None
                and publication_year > year_to
            ):
                continue

            year_filtered_papers.append(paper)

        print(f"Year From: {year_from}")
        print(f"Year To: {year_to}")

    else:
        print("No year restriction applied.")

    print(
        f"Papers before year filter: {len(papers)}"
    )

    print(
        f"Papers after year filter: "
        f"{len(year_filtered_papers)}"
    )

    if not year_filtered_papers:
        return {
            "project_id": project_id,
            "model1": discovery_result,
            "candidate_collection": candidate_result,
            "abstract_retrieval": abstract_result,
            "fulltext_preparation": {
                "attempted": 0,
                "processed": 0,
                "errors": [],
            },
            "year_filter": {
                "year_from": year_from,
                "year_to": year_to,
                "before": len(papers),
                "after": 0,
            },
            "prefilter": {
                "total_input": 0,
                "total_selected": 0,
                "papers": []
            },
            "model2": {
                "total_screened": 0,
                "ai_calls": 0,
                "cached_results": 0,
                "results": [],
                "included": [],
                "uncertain": [],
                "excluded": []
            },
            "included": [],
            "uncertain": [],
            "excluded": [],
            "shortlist": [],
            "included_count": 0,
            "uncertain_count": 0,
            "excluded_count": 0,
            "sources": sources or ["pubmed"],
            "restriction": restriction,
            "limitations": limitations,
        }

    # =========================================================
    # PREFILTER
    # =========================================================

    print()
    print("=" * 70)
    print("STEP 6: LOCAL RELEVANCE PRE-FILTER")
    print("=" * 70)

    if keywords:
        prefilter_keywords = keywords
    else:
        prefilter_keywords = []

        if research_topic:
            prefilter_keywords.append(research_topic)

        if research_question:
            prefilter_keywords.append(research_question)

        if population:
            prefilter_keywords.append(population)

        if intervention:
            prefilter_keywords.append(intervention)

        if comparison:
            prefilter_keywords.append(comparison)

        if outcome:
            prefilter_keywords.append(outcome)

        if study_type:
            prefilter_keywords.append(study_type)

    prefilter_result = prefilter_papers(
        papers=year_filtered_papers,
        keywords=prefilter_keywords,
        max_papers=3
    )

    prefiltered_papers = prefilter_result["papers"]

    prefiltered_papers = prefiltered_papers[:3]

    print(
        f"Input papers: "
        f"{prefilter_result['total_input']}"
    )

    print(
        f"Selected for Model 2: "
        f"{len(prefiltered_papers)}"
    )

    # =========================================================
    # MODEL 2
    # =========================================================

    print()
    print("=" * 70)
    print("STEP 7: AI MODEL 2 - PICOS SCREENING")
    print("=" * 70)

    prefiltered_paper_ids = [
        paper["paper_id"]
        for paper in prefiltered_papers
    ]

    fulltext_preparation = {
        "attempted": 0,
        "processed": 0,
        "errors": [],
    }
    for paper in (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id,
            Paper.id.in_(prefiltered_paper_ids),
            Paper.pdf_path.isnot(None),
        )
        .all()
    ):
        fulltext_preparation["attempted"] += 1
        try:
            from ..services.fulltext_pipeline_service import (
                process_paper_fulltext,
            )

            process_paper_fulltext(
                db=db,
                project_id=project_id,
                paper_id=paper.id,
                pdf_path=paper.pdf_path,
            )
            fulltext_preparation["processed"] += 1
        except Exception as error:
            db.rollback()
            fulltext_preparation["errors"].append({
                "paper_id": paper.id,
                "title": paper.title,
                "error": str(error),
            })

    screened_results = screen_project_papers(
        db=db,
        project_id=project_id,
        population=population or "",
        intervention=intervention or "",
        comparison=comparison or "",
        outcome=outcome or "",
        study_type=study_type or "",
        restriction=restriction,
        limitations=limitations,
        paper_ids=prefiltered_paper_ids
    )

    included = [
        result for result in screened_results
        if result["decision"] == "Include"
    ]
    uncertain = [
        result for result in screened_results
        if result["decision"] == "Uncertain"
    ]
    excluded = [
        result for result in screened_results
        if result["decision"] == "Exclude"
    ]

    shortlist = included + uncertain
    model2_results = {
        "total_screened": len(screened_results),
        "ai_calls": sum(not result.get("cached", False) for result in screened_results),
        "cached_results": sum(result.get("cached", False) for result in screened_results),
        "results": screened_results,
        "included": included,
        "uncertain": uncertain,
        "excluded": excluded,
        "included_count": len(included),
        "uncertain_count": len(uncertain),
        "excluded_count": len(excluded),
        "shortlist": shortlist,
    }

    print()
    print("=" * 70)
    print("MODEL 2 COMPLETED")
    print("=" * 70)

    print(f"Included: {len(included)}")
    print(f"Uncertain: {len(uncertain)}")
    print(f"Excluded: {len(excluded)}")

    return {
        "project_id": project_id,
        "model1": discovery_result,
        "candidate_collection": candidate_result,
        "abstract_retrieval": abstract_result,
        "fulltext_preparation": fulltext_preparation,
        "year_filter": {
            "year_from": year_from,
            "year_to": year_to,
            "before": len(papers),
            "after": len(year_filtered_papers)
        },
        "prefilter": prefilter_result,
        "model2": model2_results,
        "included": included,
        "uncertain": uncertain,
        "excluded": excluded,
        "shortlist": shortlist,
        "included_count": len(included),
        "uncertain_count": len(uncertain),
        "excluded_count": len(excluded),
        "restriction": restriction,
        "limitations": limitations,
        "sources": sources or ["pubmed"],
    }