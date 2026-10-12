from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore

from ..models import Paper
from ..services.literature_source_service import (
    search_arxiv,
    search_crossref,
    search_google_scholar,
    search_ieee_xplore,
    search_openalex,
)
from ..services.pubmed_service import (
    search_pubmed,
    fetch_pubmed_details,
    fetch_pubmed_abstracts
)

MAX_PARALLEL_SOURCE_SEARCHES = 8
_PUBMED_SEARCH_LIMIT = Semaphore(1)


def collect_candidate_papers(
    queries: list[str],
    max_results_per_query: int = 10,
    sources: list[str] | None = None,
):
    """
    Collect candidate papers from the selected literature indexes.

    Duplicate DOI, PubMed ID, and title records are removed.
    """

    if not queries:
        raise ValueError(
            "No search queries provided."
        )

    selected_sources = sources or ["pubmed"]
    searchers = {
        "pubmed": _search_pubmed,
        "openalex": search_openalex,
        "crossref": search_crossref,
        "arxiv": search_arxiv,
        "ieee_xplore": search_ieee_xplore,
        "google_scholar": search_google_scholar,
    }
    all_papers = []
    seen_keys = set()
    source_counts = {source: 0 for source in selected_sources}
    source_errors = []

    unsupported_sources = set(selected_sources) - set(searchers)
    if unsupported_sources:
        raise ValueError(
            "Unsupported literature source(s): "
            + ", ".join(sorted(unsupported_sources))
        )

    jobs = [
        (query, source)
        for query in queries
        for source in selected_sources
    ]

    def run_search(job):
        query, source = job
        try:
            if source == "pubmed":
                with _PUBMED_SEARCH_LIMIT:
                    papers = searchers[source](query, max_results_per_query)
            else:
                papers = searchers[source](query, max_results_per_query)
            return query, source, papers, None
        except Exception as error:
            return query, source, [], str(error)

    worker_count = min(MAX_PARALLEL_SOURCE_SEARCHES, len(jobs))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        search_results = list(executor.map(run_search, jobs))

    for query, source, papers, error in search_results:
        if error:
            source_errors.append(f"{source}: {error}")
            continue

        for paper in papers:
            paper["discovery_query"] = query
            paper.setdefault("source", source.title())

            pubmed_id = paper.get("pubmed_id")
            doi = (paper.get("doi") or "").lower().replace(
                "https://doi.org/", ""
            ).replace("http://doi.org/", "")
            title_key = " ".join(
                (paper.get("title") or "").lower().split()
            )
            key = (
                f"doi:{doi}"
                if doi
                else f"pmid:{pubmed_id}"
                if pubmed_id
                else f"title:{title_key}"
            )

            if not title_key or key in seen_keys:
                continue

            seen_keys.add(key)
            source_counts[source] += 1
            all_papers.append(paper)

    if not all_papers and source_errors:
        raise RuntimeError(
            "Candidate search failed for all selected sources. "
            + " | ".join(dict.fromkeys(source_errors))
        )
    if not all_papers:
        raise ValueError(
            "No papers were found. Broaden your topic or year range, "
            "or select another available literature source."
        )

    return {
        "total_candidates": len(
            all_papers
        ),
        "sources": selected_sources,
        "source_counts": source_counts,
        "source_errors": list(dict.fromkeys(source_errors)),
        "papers": all_papers
    }


def _search_pubmed(query: str, max_results: int) -> list[dict]:
    pubmed_ids = search_pubmed(
        query=query,
        max_results=max_results
    )
    return fetch_pubmed_details(pubmed_ids) if pubmed_ids else []


def save_candidate_papers(
    db,
    project_id: int,
    papers: list[dict]
):
    """
    Save candidate papers into MySQL.

    Existing papers are reused.
    """

    saved_papers = []
    project_papers = (
        db.query(Paper)
        .filter(Paper.project_id == project_id)
        .all()
    )
    by_pubmed_id = {
        paper.pubmed_id: paper
        for paper in project_papers
        if paper.pubmed_id
    }
    by_doi = {
        paper.doi.lower().replace("https://doi.org/", "").replace(
            "http://doi.org/", ""
        ): paper
        for paper in project_papers
        if paper.doi
    }
    by_title = {
        " ".join((paper.title or "").lower().split()): paper
        for paper in project_papers
        if paper.title
    }

    for paper_data in papers:
        pubmed_id = paper_data.get(
            "pubmed_id"
        )

        title = paper_data.get("title")
        if not title:
            continue

        doi = paper_data.get("doi")
        normalized_doi = (
            doi.lower()
            .replace("https://doi.org/", "")
            .replace("http://doi.org/", "")
            if doi
            else None
        )
        title_key = " ".join(title.lower().split())
        existing_paper = (
            by_pubmed_id.get(pubmed_id)
            if pubmed_id
            else None
        ) or (
            by_doi.get(normalized_doi)
            if normalized_doi
            else None
        ) or by_title.get(title_key)

        if existing_paper:
            for field in (
                "authors",
                "abstract",
                "publication_year",
                "journal",
                "doi",
                "url",
                "source",
            ):
                if getattr(existing_paper, field) in (None, ""):
                    value = paper_data.get(field)
                    if value is not None:
                        setattr(existing_paper, field, value)
            saved_papers.append(
                existing_paper
            )
            continue

        paper = Paper(
            project_id=project_id,
            pubmed_id=pubmed_id,
            title=title,
            authors=paper_data.get("authors"),
            abstract=paper_data.get("abstract"),
            publication_year=paper_data.get("publication_year"),
            journal=paper_data.get("journal"),
            doi=doi,
            source=paper_data.get("source"),
            url=paper_data.get("url"),
        )

        db.add(paper)
        db.flush()
        saved_papers.append(
            paper
        )
        if pubmed_id:
            by_pubmed_id[pubmed_id] = paper
        if normalized_doi:
            by_doi[normalized_doi] = paper
        by_title[title_key] = paper

    db.commit()

    return saved_papers


def update_candidate_abstracts(
    db,
    project_id: int,
    paper_ids: list[int] | None = None
):
    """
    Retrieve PubMed abstracts.

    If paper_ids is supplied:
        Only those papers are processed.

    If paper_ids is not supplied:
        All PubMed papers in the project are processed.

    The pipeline should normally provide paper_ids.
    """

    query = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id,
            Paper.pubmed_id.isnot(None)
        )
    )

    # ---------------------------------------------------------
    # IMPORTANT:
    # Restrict processing to the current pipeline batch.
    # ---------------------------------------------------------

    if paper_ids is not None:

        if not paper_ids:

            return {
                "total_papers": 0,
                "updated": 0,
                "missing_abstract": 0
            }

        query = query.filter(
            Paper.id.in_(paper_ids)
        )

    papers = query.all()

    if not papers:

        return {
            "total_papers": 0,
            "updated": 0,
            "missing_abstract": 0
        }

    pubmed_ids = [
        paper.pubmed_id
        for paper in papers
        if paper.pubmed_id
    ]

    if not pubmed_ids:

        return {
            "total_papers": len(papers),
            "updated": 0,
            "missing_abstract": len(papers)
        }

    print(
        f"\nFetching abstracts for "
        f"{len(pubmed_ids)} papers..."
    )

    abstracts = fetch_pubmed_abstracts(
        pubmed_ids
    )

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