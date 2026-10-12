from sqlalchemy.orm import Session

from ..ai.discovery_service import generate_search_queries
from ..ai.screening_model2_service import screen_project_papers
from ..services.candidate_service import (
    collect_candidate_papers,
    save_candidate_papers,
    update_candidate_abstracts
)
from ..services.shortlist_service import get_model2_shortlist


def run_literature_pipeline(
    db: Session,
    project_id: int,
    keyword: str,
    domain: str,
    population: str,
    intervention: str,
    comparison: str,
    outcome: str,
    study_type: str,
    max_queries: int = 1,
    max_results_per_query: int = 5
):
    # ==========================================
    # STEP 1 — MODEL 1: DISCOVERY
    # ==========================================

    print("\n====================================")
    print("STEP 1 — MODEL 1 DISCOVERY")
    print("====================================")

    discovery_result = generate_search_queries(
        keyword=keyword,
        domain=domain,
        max_queries=max_queries
    )

    queries = discovery_result["queries"]

    print("\nGenerated Queries:")
    for query in queries:
        print("-", query)

    # ==========================================
    # STEP 2 — CANDIDATE COLLECTION
    # ==========================================

    print("\n====================================")
    print("STEP 2 — CANDIDATE COLLECTION")
    print("====================================")

    candidate_result = collect_candidate_papers(
        queries=queries,
        max_results_per_query=max_results_per_query
    )

    candidates = candidate_result["papers"]

    print(
        "Candidates found:",
        candidate_result["total_candidates"]
    )

    # ==========================================
    # STEP 3 — SAVE CANDIDATES
    # ==========================================

    print("\n====================================")
    print("STEP 3 — SAVE CANDIDATES")
    print("====================================")

    saved_papers = save_candidate_papers(
        db=db,
        project_id=project_id,
        papers=candidates
    )

    print(
        "Candidates saved:",
        len(saved_papers)
    )

    # ==========================================
    # STEP 4 — ABSTRACT RETRIEVAL
    # ==========================================

    print("\n====================================")
    print("STEP 4 — ABSTRACT RETRIEVAL")
    print("====================================")

    abstract_result = update_candidate_abstracts(
        db=db,
        project_id=project_id
    )

    print(
        "Abstracts updated:",
        abstract_result["updated"]
    )

    print(
        "Missing abstracts:",
        abstract_result["missing_abstract"]
    )

    # ==========================================
    # STEP 5 — MODEL 2 SCREENING
    # ==========================================

    print("\n====================================")
    print("STEP 5 — MODEL 2 PICOS SCREENING")
    print("====================================")

    screening_results = screen_project_papers(
        db=db,
        project_id=project_id,
        population=population,
        intervention=intervention,
        comparison=comparison,
        outcome=outcome,
        study_type=study_type
    )

    # ==========================================
    # STEP 6 — SHORTLIST
    # ==========================================

    print("\n====================================")
    print("STEP 6 — MODEL 2 SHORTLIST")
    print("====================================")

    shortlist = get_model2_shortlist(
        db=db,
        project_id=project_id
    )

    print(
        "Included:",
        shortlist["included_count"]
    )

    print(
        "Uncertain:",
        shortlist["uncertain_count"]
    )

    print(
        "Excluded:",
        shortlist["excluded_count"]
    )

    # ==========================================
    # FINAL PIPELINE RESULT
    # ==========================================

    return {
        "project_id": project_id,

        "model1": {
            "research_topic": keyword,
            "queries": queries,
            "query_count": len(queries)
        },

        "candidate_collection": {
            "total_candidates": candidate_result["total_candidates"],
            "saved_candidates": len(saved_papers)
        },

        "abstract_retrieval": abstract_result,

        "model2": {
            "screened_papers": len(screening_results),
            "included": shortlist["included_count"],
            "uncertain": shortlist["uncertain_count"],
            "excluded": shortlist["excluded_count"]
        },

        "shortlist": shortlist
    }