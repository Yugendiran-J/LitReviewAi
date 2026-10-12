from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..dependencies import get_current_user
from ..models import HumanFeedback, Paper, ResearchProject, User


router = APIRouter(
    prefix="/human-feedback",
    tags=["Human Validation"]
)


# ============================================================
# REQUEST MODEL
# ============================================================

class HumanFeedbackRequest(BaseModel):

    paper_id: int

    ai_decision: str

    human_decision: str

    comment: str | None = None


# ============================================================
# SUBMIT HUMAN FEEDBACK
# ============================================================

@router.post("/")
def submit_human_feedback(
    feedback: HumanFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # --------------------------------------------------------
    # Validate decision
    # --------------------------------------------------------

    valid_decisions = {
        "Include",
        "Exclude",
        "Uncertain"
    }

    if feedback.ai_decision not in valid_decisions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid AI decision. "
                "Use Include, Exclude, or Uncertain."
            )
        )

    if feedback.human_decision not in valid_decisions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid human decision. "
                "Use Include, Exclude, or Uncertain."
            )
        )

    # --------------------------------------------------------
    # Check paper
    # --------------------------------------------------------

    paper = (
        db.query(Paper)
        .join(
            ResearchProject,
            ResearchProject.id == Paper.project_id,
        )
        .filter(
            Paper.id == feedback.paper_id,
            ResearchProject.user_id == current_user.id,
        )
        .first()
    )

    if not paper:

        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    # --------------------------------------------------------
    # Create feedback
    # --------------------------------------------------------

    human_feedback = HumanFeedback(
        paper_id=feedback.paper_id,
        original_decision=feedback.ai_decision,
        corrected_decision=feedback.human_decision,
        feedback_text=feedback.comment,
        reviewer_name=current_user.name,
    )

    db.add(
        human_feedback
    )

    db.commit()

    db.refresh(
        human_feedback
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "success": True,
        "message": "Human feedback saved successfully.",
        "feedback_id": human_feedback.id,
        "paper_id": feedback.paper_id,
        "ai_decision": feedback.ai_decision,
        "human_decision": feedback.human_decision,
        "comment": feedback.comment
    }