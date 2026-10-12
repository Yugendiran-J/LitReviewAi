from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    Paper,
    ScreeningResult,
    HumanFeedback,
    User
)
from ..dependencies import get_current_user
from ..schemas import (
    HumanFeedbackCreate,
    HumanFeedbackResponse
)


router = APIRouter(
    prefix="/projects/{project_id}/feedback",
    tags=["Human Feedback"]
)


@router.post(
    "/papers/{paper_id}",
    response_model=HumanFeedbackResponse
)
def create_feedback(
    project_id: int,
    paper_id: int,
    feedback_data: HumanFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check project ownership
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

    # Check paper
    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.project_id == project_id
        )
        .first()
    )

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    # Validate corrected decision
    allowed_decisions = [
        "Include",
        "Exclude",
        "Uncertain"
    ]

    if feedback_data.corrected_decision not in allowed_decisions:
        raise HTTPException(
            status_code=400,
            detail="corrected_decision must be Include, Exclude, or Uncertain"
        )

    # Get latest AI screening result
    screening_result = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.paper_id == paper_id
        )
        .order_by(ScreeningResult.id.desc())
        .first()
    )

    if screening_result is None:
        raise HTTPException(
            status_code=400,
            detail="No AI screening result found for this paper"
        )

    # Save human feedback
    feedback = HumanFeedback(
        paper_id=paper_id,
        original_decision=screening_result.decision,
        corrected_decision=feedback_data.corrected_decision,
        feedback_text=feedback_data.feedback_text,
        reviewer_name=feedback_data.reviewer_name
    )
    # Update screening result with human decision
    screening_result.decision = feedback_data.corrected_decision

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback