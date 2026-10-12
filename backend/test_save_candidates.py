from app.database import SessionLocal
from app.ai.discovery_service import generate_search_queries
from app.services.candidate_service import (
    collect_candidate_papers,
    save_candidate_papers
)


PROJECT_ID = 2


db = SessionLocal()

try:

    print("\nSTEP 1: AI MODEL 1")
    print("===================")

    query_result = generate_search_queries(
        keyword="AI-powered systematic literature review",
        domain="Computer Science",
        max_queries=5
    )

    queries = query_result["queries"]

    for index, query in enumerate(queries, start=1):
        print(f"{index}. {query}")


    print("\nSTEP 2: PUBMED CANDIDATE COLLECTION")
    print("====================================")

    candidate_result = collect_candidate_papers(
        queries=queries,
        max_results_per_query=10
    )

    papers = candidate_result["papers"]

    print(
        f"\nUnique candidate papers: {len(papers)}"
    )


    print("\nSTEP 3: SAVING TO MYSQL")
    print("========================")

    saved_papers = save_candidate_papers(
        db=db,
        project_id=PROJECT_ID,
        papers=papers
    )

    print(
        f"Successfully saved/loaded: {len(saved_papers)} papers"
    )


finally:

    db.close()