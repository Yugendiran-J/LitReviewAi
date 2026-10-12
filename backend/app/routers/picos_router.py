from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PICOSCriteria, ResearchProject, User
from ..schemas import PICOSCreate, PICOSResponse, PICOSUpdate
from ..dependencies import get_current_user


router = APIRouter(
    prefix="/projects/{project_id}/picos",
    tags=["PICOS"]
)


@router.post("/")
def create_picos(
    project_id: int,
    picos_data: PICOSCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    picos = PICOSCriteria(
        project_id=project_id,
        population=picos_data.population,
        intervention=picos_data.intervention,
        comparison=picos_data.comparison,
        outcome=picos_data.outcome,
        study_type=picos_data.study_type,
        additional_criteria=picos_data.additional_criteria
    )

    db.add(picos)
    db.commit()
    db.refresh(picos)

    return picos

@router.get("/", response_model=list[PICOSResponse])
def get_picos(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    picos = (
        db.query(PICOSCriteria)
        .filter(PICOSCriteria.project_id == project_id)
        .all()
    )

    return picos


@router.put("/{picos_id}", response_model=PICOSResponse)
def update_picos(
    project_id: int,
    picos_id: int,
    picos_data: PICOSUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    picos = (
        db.query(PICOSCriteria)
        .filter(
            PICOSCriteria.id == picos_id,
            PICOSCriteria.project_id == project_id
        )
        .first()
    )

    if picos is None:
        raise HTTPException(
            status_code=404,
            detail="PICOS criteria not found"
        )

    if picos_data.population is not None:
        picos.population = picos_data.population

    if picos_data.intervention is not None:
        picos.intervention = picos_data.intervention

    if picos_data.comparison is not None:
        picos.comparison = picos_data.comparison

    if picos_data.outcome is not None:
        picos.outcome = picos_data.outcome

    if picos_data.study_type is not None:
        picos.study_type = picos_data.study_type

    if picos_data.additional_criteria is not None:
        picos.additional_criteria = picos_data.additional_criteria

    db.commit()
    db.refresh(picos)

    return picos

@router.delete("/{picos_id}")
def delete_picos(
    project_id: int,
    picos_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    picos = (
        db.query(PICOSCriteria)
        .filter(
            PICOSCriteria.id == picos_id,
            PICOSCriteria.project_id == project_id
        )
        .first()
    )

    if picos is None:
        raise HTTPException(
            status_code=404,
            detail="PICOS criteria not found"
        )

    db.delete(picos)
    db.commit()

    return {
        "message": "PICOS criteria deleted successfully"
    }