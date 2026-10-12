from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    Paper,
    ScreeningResult,
    ExtractedData,
    HumanFeedback,
    User
)
from ..dependencies import get_current_user
from ..schemas import DashboardResponse


router = APIRouter(
    prefix="/projects",
    tags=["Dashboard"]
)


@router.get(
    "/{project_id}/dashboard",
    response_model=DashboardResponse
)
def get_dashboard(
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
    # 2. Get project papers
    # --------------------------------
    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    total_papers = len(papers)

    included_papers = 0
    excluded_papers = 0
    uncertain_papers = 0
    not_screened = 0

    papers_with_pdf = 0
    extracted_papers = 0

    # --------------------------------
    # 3. Calculate paper statistics
    # --------------------------------
    for paper in papers:

        # PDF status
        if paper.pdf_path:
            papers_with_pdf += 1

        # Latest screening result
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
            not_screened += 1
        else:
            decision = (
                screening.decision or ""
            ).strip().lower()

            if decision == "include":
                included_papers += 1

            elif decision == "exclude":
                excluded_papers += 1

            elif decision == "uncertain":
                uncertain_papers += 1

            else:
                not_screened += 1

        # Extraction status
        extraction = (
            db.query(ExtractedData)
            .filter(
                ExtractedData.paper_id == paper.id
            )
            .first()
        )

        if extraction is not None:
            extracted_papers += 1

    # --------------------------------
    # 4. Extraction statistics
    # --------------------------------
    not_extracted_papers = (
        total_papers - extracted_papers
    )

    # --------------------------------
    # 5. Human feedback
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

    for feedback in feedback_records:

        original = (
            feedback.original_decision or ""
        ).strip()

        corrected = (
            feedback.corrected_decision or ""
        ).strip()

        if original == corrected:
            accepted_feedback += 1
        else:
            corrected_feedback += 1

    # --------------------------------
    # 6. Return dashboard data
    # --------------------------------
    return {
        "project_id": project.id,
        "project_title": project.title,
        "research_question": project.research_question,
        "status": project.status,

        "total_papers": total_papers,

        "included_papers": included_papers,
        "excluded_papers": excluded_papers,
        "uncertain_papers": uncertain_papers,
        "not_screened": not_screened,

        "papers_with_pdf": papers_with_pdf,

        "extracted_papers": extracted_papers,
        "not_extracted_papers": not_extracted_papers,

        "total_feedback": total_feedback,
        "accepted_feedback": accepted_feedback,
        "corrected_feedback": corrected_feedback
    }