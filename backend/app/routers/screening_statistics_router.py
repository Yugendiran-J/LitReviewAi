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
from ..schemas import ScreeningStatisticsResponse


router = APIRouter(
    prefix="/projects/{project_id}/screening",
    tags=["Screening Statistics"]
)


@router.get(
    "/statistics",
    response_model=ScreeningStatisticsResponse
)
def get_screening_statistics(
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

    included = 0
    excluded = 0
    uncertain = 0
    not_screened = 0

    # --------------------------------
    # 3. Count latest decision
    # --------------------------------
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
            not_screened += 1
            continue

        decision = (
            screening.decision or ""
        ).strip().lower()

        if decision == "include":
            included += 1

        elif decision == "exclude":
            excluded += 1

        elif decision == "uncertain":
            uncertain += 1

        else:
            not_screened += 1

    # --------------------------------
    # 4. Return statistics
    # --------------------------------
    return {
        "project_id": project_id,
        "total_papers": total_papers,
        "included": included,
        "excluded": excluded,
        "uncertain": uncertain,
        "not_screened": not_screened
    }