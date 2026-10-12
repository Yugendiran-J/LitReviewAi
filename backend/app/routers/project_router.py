from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ResearchProject, User
from ..schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from ..dependencies import get_current_user


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = ResearchProject(
        user_id=current_user.id,
        title=project_data.title,
        research_question=project_data.research_question,
        description=project_data.description,
        domain=project_data.domain
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = (
        db.query(ResearchProject)
        .filter(ResearchProject.user_id == current_user.id)
        .all()
    )

    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
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
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
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
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if project_data.title is not None:
        project.title = project_data.title

    if project_data.research_question is not None:
        project.research_question = project_data.research_question

    if project_data.description is not None:
        project.description = project_data.description

    if project_data.domain is not None:
        project.domain = project_data.domain

    if project_data.status is not None:
        project.status = project_data.status

    db.commit()
    db.refresh(project)

    return project

@router.delete("/{project_id}")
def delete_project(
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
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }