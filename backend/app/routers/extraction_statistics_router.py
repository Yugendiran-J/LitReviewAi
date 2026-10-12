from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    Paper,
    ExtractedData,
    User
)
from ..dependencies import get_current_user
from ..schemas import ExtractionStatisticsResponse


router = APIRouter(
    prefix="/projects/{project_id}/extraction",
    tags=["Extraction Statistics"]
)


@router.get(
    "/statistics",
    response_model=ExtractionStatisticsResponse
)
def get_extraction_statistics(
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
    # 2. Total papers
    # --------------------------------
    total_papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .count()
    )

    # --------------------------------
    # 3. Papers with extraction
    # --------------------------------
    extracted_papers = (
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
    # 4. Papers without extraction
    # --------------------------------
    not_extracted_papers = (
        total_papers - extracted_papers
    )

    # --------------------------------
    # 5. Return statistics
    # --------------------------------
    return {
        "project_id": project_id,
        "total_papers": total_papers,
        "extracted_papers": extracted_papers,
        "not_extracted_papers": not_extracted_papers
    }

