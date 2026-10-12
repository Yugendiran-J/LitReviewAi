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
from ..schemas import ProjectSummaryResponse


router = APIRouter(
    prefix="/projects",
    tags=["Project Summary"]
)


@router.get(
    "/{project_id}/summary",
    response_model=ProjectSummaryResponse
)
def get_project_summary(
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
    # 2. Get all papers
    # --------------------------------
    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    total_papers = len(papers)

    # --------------------------------
    # 3. Screening statistics
    # --------------------------------
    included_papers = 0
    excluded_papers = 0
    uncertain_papers = 0

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

        if decision == "include":
            included_papers += 1

        elif decision == "exclude":
            excluded_papers += 1

        elif decision == "uncertain":
            uncertain_papers += 1

    # --------------------------------
    # 4. Papers with PDF
    # --------------------------------
    papers_with_pdf = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id,
            Paper.pdf_path.isnot(None)
        )
        .count()
    )

    # --------------------------------
    # 5. Papers with extraction
    # --------------------------------
    papers_with_extraction = (
        db.query(Paper)
        .join(
            ExtractedData,
            ExtractedData.paper_id == Paper.id
        )
        .filter(
            Paper.project_id == project_id
        )
        .distinct()
        .count()
    )

    # --------------------------------
    # 6. Human feedback count
    # --------------------------------
    total_feedback = (
        db.query(HumanFeedback)
        .join(
            Paper,
            HumanFeedback.paper_id == Paper.id
        )
        .filter(
            Paper.project_id == project_id
        )
        .count()
    )

    # --------------------------------
    # 7. Return summary
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

        "papers_with_pdf": papers_with_pdf,
        "papers_with_extraction": papers_with_extraction,
        "total_feedback": total_feedback
    }