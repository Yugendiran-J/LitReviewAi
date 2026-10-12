from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ResearchProject, User, Paper
from ..schemas import LiteratureSearchRequest, LiteratureSearchResponse
from ..dependencies import get_current_user
from ..services.pubmed_service import (
    search_pubmed,
    fetch_pubmed_details
)

router = APIRouter(
    prefix="/projects/{project_id}/search",
    tags=["Literature Search"]
)


@router.post(
    "/pubmed",
    response_model=list[LiteratureSearchResponse]
)
def search_literature(
    project_id: int,
    search_data: LiteratureSearchRequest,
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

    # Validate result count
    if search_data.max_results < 1:
        raise HTTPException(
            status_code=400,
            detail="max_results must be at least 1"
        )

    if search_data.max_results > 100:
        raise HTTPException(
            status_code=400,
            detail="max_results cannot exceed 100"
        )

    try:
        # Search PubMed
        pubmed_ids = search_pubmed(
            search_data.query,
            search_data.max_results
        )

        # Get paper details
        papers = fetch_pubmed_details(pubmed_ids)

        response = []

        for paper_data in papers:

            pubmed_id = paper_data["pubmed_id"]

            # Check if paper already exists
            existing_paper = (
                db.query(Paper)
                .filter(
                    Paper.project_id == project_id,
                    Paper.pubmed_id == pubmed_id
                )
                .first()
            )

            if existing_paper:
                response.append({
                    **paper_data,
                    "saved": True,
                    "paper_id": existing_paper.id
                })
                continue

            # Create new paper
            new_paper = Paper(
                project_id=project_id,
                pubmed_id=pubmed_id,
                title=paper_data["title"],
                authors=paper_data["authors"],
                publication_year=paper_data["publication_year"],
                journal=paper_data["journal"],
                source=paper_data["source"],
                url=paper_data["url"]
            )

            db.add(new_paper)
            db.flush()

            response.append({
                **paper_data,
                "saved": True,
                "paper_id": new_paper.id
            })

        db.commit()

        return response

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"PubMed import failed: {str(e)}"
        )