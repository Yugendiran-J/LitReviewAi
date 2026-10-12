from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    Paper,
    PaperChunk,
    User
)
from ..dependencies import get_current_user
from ..schemas import PaperChunkResponse


router = APIRouter(
    prefix="/projects/{project_id}/papers",
    tags=["Paper Chunks"]
)


@router.get(
    "/{paper_id}/chunks",
    response_model=list[PaperChunkResponse]
)
def get_paper_chunks(
    project_id: int,
    paper_id: int,
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

    # Get chunks
    chunks = (
        db.query(PaperChunk)
        .filter(
            PaperChunk.paper_id == paper_id
        )
        .order_by(
            PaperChunk.chunk_index.asc()
        )
        .all()
    )

    return chunks