from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    Paper,
    HumanFeedback,
    User
)
from ..dependencies import get_current_user
from ..schemas import FeedbackStatisticsResponse


router = APIRouter(
    prefix="/projects/{project_id}/feedback",
    tags=["Feedback Statistics"]
)


@router.get(
    "/statistics",
    response_model=FeedbackStatisticsResponse
)
def get_feedback_statistics(
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

    # --------------------------------
    # 2. Get feedback records
    # --------------------------------
    feedback_records = (
        db.query(HumanFeedback)
        .join(
            Paper,
            HumanFeedback.paper_id == Paper.id
        )
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    total_feedback = len(feedback_records)

    accepted_feedback = 0
    corrected_feedback = 0

    # --------------------------------
    # 3. Count feedback types
    # --------------------------------
    for feedback in feedback_records:

        original = (
            feedback.original_decision
            or ""
        ).strip()

        corrected = (
            feedback.corrected_decision
            or ""
        ).strip()

        if original == corrected:
            accepted_feedback += 1
        else:
            corrected_feedback += 1

    # --------------------------------
    # 4. Return statistics
    # --------------------------------
    return {
        "project_id": project_id,
        "total_feedback": total_feedback,
        "accepted_feedback": accepted_feedback,
        "corrected_feedback": corrected_feedback
    }