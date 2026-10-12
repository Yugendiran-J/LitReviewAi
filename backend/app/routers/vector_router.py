from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ResearchProject, Paper, User
from ..dependencies import get_current_user
from ..schemas import SemanticSearchRequest, SemanticSearchResult
from ..services.vector_service import search_vector_index


router = APIRouter(
    prefix="/projects/{project_id}/papers",
    tags=["Semantic Search"]
)


@router.post(
    "/{paper_id}/search",
    response_model=list[SemanticSearchResult]
)
def semantic_search(
    project_id: int,
    paper_id: int,
    request: SemanticSearchRequest,
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

    # Check paper belongs to project
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

    # Validate query
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    # Validate top_k
    if request.top_k < 1:
        raise HTTPException(
            status_code=400,
            detail="top_k must be at least 1"
        )

    try:
        results = search_vector_index(
            paper_id=paper_id,
            query=request.query,
            top_k=request.top_k
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Vector index not found. Create the vector index first."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {str(e)}"
        )

    return results