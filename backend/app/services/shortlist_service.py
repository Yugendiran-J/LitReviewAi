from sqlalchemy.orm import Session

from ..models import Paper, ScreeningResult


def get_model2_shortlist(
    db: Session,
    project_id: int
):
    """
    Get papers selected after AI Model 2 screening.

    Include    -> Full-text analysis
    Uncertain  -> Human review
    Exclude    -> Not shortlisted
    """

    results = (
        db.query(
            Paper,
            ScreeningResult
        )
        .join(
            ScreeningResult,
            ScreeningResult.paper_id == Paper.id
        )
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    included = []
    uncertain = []
    excluded = []

    for paper, screening in results:

        paper_data = {
            "paper_id": paper.id,
            "pubmed_id": paper.pubmed_id,
            "title": paper.title,
            "authors": paper.authors,
            "publication_year": paper.publication_year,
            "journal": paper.journal,
            "url": paper.url,
            "decision": screening.decision,
            "confidence": screening.confidence_score,
            "reason": screening.reason
        }

        if screening.decision == "Include":
            included.append(paper_data)

        elif screening.decision == "Uncertain":
            uncertain.append(paper_data)

        elif screening.decision == "Exclude":
            excluded.append(paper_data)

    return {
        "project_id": project_id,
        "total_screened": len(results),
        "included": included,
        "uncertain": uncertain,
        "excluded": excluded,
        "included_count": len(included),
        "uncertain_count": len(uncertain),
        "excluded_count": len(excluded)
    }