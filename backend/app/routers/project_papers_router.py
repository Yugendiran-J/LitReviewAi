from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    Paper,
    ScreeningResult,
    ExtractedData,
    User
)
from ..dependencies import get_current_user
from ..schemas import ProjectPaperResponse


router = APIRouter(
    prefix="/projects",
    tags=["Project Papers"]
)


@router.get(
    "/{project_id}/papers/list",
    response_model=list[ProjectPaperResponse]
)
def get_project_papers(
    project_id: int,
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

    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .order_by(Paper.id.desc())
        .all()
    )

    results = []

    for paper in papers:

        screening = (
            db.query(ScreeningResult)
            .filter(
                ScreeningResult.paper_id == paper.id
            )
            .order_by(ScreeningResult.id.desc())
            .first()
        )

        extraction = (
            db.query(ExtractedData)
            .filter(
                ExtractedData.paper_id == paper.id
            )
            .order_by(ExtractedData.id.desc())
            .first()
        )

        results.append({
            "paper_id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "publication_year": paper.publication_year,
            "journal": paper.journal,
            "source": paper.source,

            "screening_decision": (
                screening.decision
                if screening else None
            ),

            "screening_confidence": (
                screening.confidence_score
                if screening else None
            ),

            "screening_reason": (
                screening.reason
                if screening else None
            ),

            "has_pdf": bool(paper.pdf_path),

            "has_extraction": extraction is not None
        })

    return results