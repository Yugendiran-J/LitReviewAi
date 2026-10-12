from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    Paper,
    ScreeningResult,
    User
)
from ..dependencies import get_current_user
from ..schemas import ScreeningReviewResponse
from ..services.confidence_service import get_confidence_level


router = APIRouter(
    prefix="/projects/{project_id}/screening",
    tags=["Human Review Queue"]
)


@router.get(
    "/review-queue",
    response_model=list[ScreeningReviewResponse]
)
def get_review_queue(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------
    # 1. Check project ownership
    # --------------------------------
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    results = []

    for paper in papers:

        screening = (
            db.query(ScreeningResult)
            .filter(
                ScreeningResult.paper_id == paper.id
            )
            .order_by(
                ScreeningResult.id.desc()
            )
            .first()
        )

        if screening is None:
            continue

        decision = (
            screening.decision
            or ""
        ).strip().lower()

        try:
            confidence = float(
                screening.confidence_score
            )
        except (ValueError, TypeError):
            confidence = 0

        confidence_level = get_confidence_level(
            screening.confidence_score
        )

        # Human review conditions
        needs_review = (
            decision == "uncertain"
            or confidence < 60
        )

        if not needs_review:
            continue

        results.append({
            "paper_id": paper.id,
            "title": paper.title,
            "abstract": paper.abstract,

            "ai_decision": screening.decision,
            "confidence_score": screening.confidence_score,
            "confidence_level": confidence_level,
            "reason": screening.reason,

            "publication_year": paper.publication_year,
            "journal": paper.journal
        })

    return results