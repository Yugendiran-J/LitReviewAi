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
from ..schemas import PaperSummaryResponse


router = APIRouter(
    prefix="/projects/{project_id}/papers",
    tags=["Paper Summary"]
)


@router.get(
    "/{paper_id}/summary",
    response_model=PaperSummaryResponse
)
def get_paper_summary(
    project_id: int,
    paper_id: int,
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
    # 2. Find paper
    # --------------------------------
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

    # --------------------------------
    # 3. Get latest screening result
    # --------------------------------
    screening = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.paper_id == paper_id
        )
        .order_by(
            ScreeningResult.id.desc()
        )
        .first()
    )

    # --------------------------------
    # 4. Get latest extraction
    # --------------------------------
    extraction = (
        db.query(ExtractedData)
        .filter(
            ExtractedData.paper_id == paper_id
        )
        .order_by(
            ExtractedData.id.desc()
        )
        .first()
    )

    # --------------------------------
    # 5. Count human feedback
    # --------------------------------
    feedback_count = (
        db.query(HumanFeedback)
        .filter(
            HumanFeedback.paper_id == paper_id
        )
        .count()
    )

    # --------------------------------
    # 6. Build response
    # --------------------------------
    return {
        "paper_id": paper.id,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "publication_year": paper.publication_year,
        "journal": paper.journal,
        "doi": paper.doi,
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

        "extraction_id": (
            extraction.id
            if extraction else None
        ),

        "population": (
            extraction.population
            if extraction else None
        ),

        "intervention": (
            extraction.intervention
            if extraction else None
        ),

        "comparison": (
            extraction.comparison
            if extraction else None
        ),

        "methodology": (
            extraction.methodology
            if extraction else None
        ),

        "dataset": (
            extraction.dataset
            if extraction else None
        ),

        "sample_size": (
            extraction.sample_size
            if extraction else None
        ),

        "results": (
            extraction.results
            if extraction else None
        ),

        "metrics": (
            extraction.metrics
            if extraction else None
        ),

        "limitations": (
            extraction.limitations
            if extraction else None
        ),

        "conclusion": (
            extraction.conclusion
            if extraction else None
        ),

        "evidence_text": (
            extraction.evidence_text
            if extraction else None
        ),

        "evidence_location": (
            extraction.evidence_location
            if extraction else None
        ),

        "extraction_confidence": (
            extraction.extraction_confidence
            if extraction else None
        ),

        "feedback_count": feedback_count
    }