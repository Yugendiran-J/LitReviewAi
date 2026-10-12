from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Paper, ResearchProject, User
from ..schemas import PaperCreate, PaperResponse, PaperUpdate
from ..dependencies import get_current_user


router = APIRouter(
    prefix="/projects/{project_id}/papers",
    tags=["Papers"]
)


@router.post("/", response_model=PaperResponse)
def create_paper(
    project_id: int,
    paper_data: PaperCreate,
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

    paper = Paper(
        project_id=project_id,
        title=paper_data.title,
        authors=paper_data.authors,
        abstract=paper_data.abstract,
        publication_year=paper_data.publication_year,
        journal=paper_data.journal,
        doi=paper_data.doi,
        url=paper_data.url,
        source=paper_data.source,
        pdf_path=paper_data.pdf_path
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return paper

@router.get("/", response_model=list[PaperResponse])
def get_papers(
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

    papers = (
        db.query(Paper)
        .filter(Paper.project_id == project_id)
        .all()
    )

    return papers

@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(
    project_id: int,
    paper_id: int,
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

    return paper

@router.put("/{paper_id}", response_model=PaperResponse)
def update_paper(
    project_id: int,
    paper_id: int,
    paper_data: PaperUpdate,
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

    if paper_data.title is not None:
        paper.title = paper_data.title

    if paper_data.authors is not None:
        paper.authors = paper_data.authors

    if paper_data.abstract is not None:
        paper.abstract = paper_data.abstract

    if paper_data.publication_year is not None:
        paper.publication_year = paper_data.publication_year

    if paper_data.journal is not None:
        paper.journal = paper_data.journal

    if paper_data.doi is not None:
        paper.doi = paper_data.doi

    if paper_data.url is not None:
        paper.url = paper_data.url

    if paper_data.source is not None:
        paper.source = paper_data.source

    if paper_data.pdf_path is not None:
        paper.pdf_path = paper_data.pdf_path

    db.commit()
    db.refresh(paper)

    return paper

@router.delete("/{paper_id}")
def delete_paper(
    project_id: int,
    paper_id: int,
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

    db.delete(paper)
    db.commit()

    return {
        "message": "Paper deleted successfully"
    }

@router.get("/", response_model=list[PaperResponse])
def get_papers(
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

    papers = (
        db.query(Paper)
        .filter(Paper.project_id == project_id)
        .order_by(Paper.id.desc())
        .all()
    )

    return papers