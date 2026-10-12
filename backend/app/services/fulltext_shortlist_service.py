from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Paper, ScreeningResult


def get_fulltext_candidates(
    db: Session,
    project_id: int,
    paper_ids: list[int] | None = None,
):
    latest_screenings = (
        db.query(
            func.max(ScreeningResult.id).label("screening_id")
        )
        .join(Paper, Paper.id == ScreeningResult.paper_id)
        .filter(Paper.project_id == project_id)
        .group_by(ScreeningResult.paper_id)
        .subquery()
    )

    results = (
        db.query(Paper, ScreeningResult)
        .join(
            ScreeningResult,
            ScreeningResult.paper_id == Paper.id,
        )
        .join(
            latest_screenings,
            ScreeningResult.id == latest_screenings.c.screening_id,
        )
        .filter(
            Paper.project_id == project_id
        )
    )
    if paper_ids is not None:
        if not paper_ids:
            return {
                "project_id": project_id,
                "included": [],
                "uncertain": [],
                "included_count": 0,
                "uncertain_count": 0,
            }
        results = results.filter(Paper.id.in_(paper_ids))
    results = results.all()

    included = []
    uncertain = []

    for paper, screening in results:

        paper_data = {
            "paper_id": paper.id,
            "pubmed_id": paper.pubmed_id,
            "title": paper.title,
            "authors": paper.authors,
            "publication_year": paper.publication_year,
            "journal": paper.journal,
            "doi": paper.doi,
            "url": paper.url,
            "decision": screening.decision,
            "confidence": screening.confidence_score,
            "reason": screening.reason
        }

        if screening.decision == "Include":
            included.append(paper_data)

        elif screening.decision == "Uncertain":
            uncertain.append(paper_data)

    return {
        "project_id": project_id,
        "included": included,
        "uncertain": uncertain,
        "included_count": len(included),
        "uncertain_count": len(uncertain)
    }