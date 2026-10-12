from .pubmed_service import search_pubmed, fetch_pubmed_details
from sqlalchemy.orm import Session
from ..models import Paper


def collect_candidate_papers(
    queries: list[str],
    max_results_per_query: int = 10
):
    if not queries:
        raise ValueError("No search queries provided")

    all_papers = []
    seen_pubmed_ids = set()

    for query in queries:

        print(f"\nSearching PubMed for:")
        print(query)

        pubmed_ids = search_pubmed(
            query=query,
            max_results=max_results_per_query
        )

        if not pubmed_ids:
            continue

        papers = fetch_pubmed_details(pubmed_ids)

        for paper in papers:

            pubmed_id = paper.get("pubmed_id")

            if not pubmed_id:
                continue

            # Remove duplicate papers
            if pubmed_id in seen_pubmed_ids:
                continue

            seen_pubmed_ids.add(pubmed_id)

            # Store the query that discovered this paper
            paper["discovery_query"] = query

            all_papers.append(paper)

    return {
        "total_candidates": len(all_papers),
        "papers": all_papers
    }

def save_candidate_papers(
    db: Session,
    project_id: int,
    papers: list[dict]
):
    saved_papers = []

    for paper_data in papers:

        pubmed_id = paper_data.get("pubmed_id")

        if not pubmed_id:
            continue

        # Check whether this paper already exists
        existing_paper = (
            db.query(Paper)
            .filter(
                Paper.project_id == project_id,
                Paper.pubmed_id == pubmed_id
            )
            .first()
        )

        if existing_paper:
            saved_papers.append(existing_paper)
            continue

        paper = Paper(
            project_id=project_id,
            pubmed_id=pubmed_id,
            title=paper_data.get("title"),
            authors=paper_data.get("authors"),
            publication_year=paper_data.get("publication_year"),
            journal=paper_data.get("journal"),
            source=paper_data.get("source"),
            url=paper_data.get("url")
        )

        db.add(paper)
        db.flush()

        saved_papers.append(paper)

    db.commit()

    return saved_papers


def update_candidate_abstracts(db, project_id: int):
    from ..models import Paper
    from .pubmed_service import fetch_pubmed_abstracts

    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id,
            Paper.pubmed_id.isnot(None)
        )
        .all()
    )

    if not papers:
        raise ValueError(
            "No PubMed candidate papers found for this project"
        )

    pubmed_ids = [
        paper.pubmed_id
        for paper in papers
    ]

    abstracts = fetch_pubmed_abstracts(pubmed_ids)

    updated_count = 0
    missing_count = 0

    for paper in papers:

        abstract = abstracts.get(
            paper.pubmed_id
        )

        if abstract:

            paper.abstract = abstract
            updated_count += 1

        else:

            missing_count += 1

    db.commit()

    return {
        "total_papers": len(papers),
        "updated": updated_count,
        "missing_abstract": missing_count
    }