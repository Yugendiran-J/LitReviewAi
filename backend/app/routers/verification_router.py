from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ResearchProject, Paper, ExtractedData, User
from ..dependencies import get_current_user
from ..schemas import VerificationRequest, VerificationResponse

from ..ai.verification_service import verify_extraction


router = APIRouter(
    prefix="/projects/{project_id}/papers",
    tags=["Evidence Verification"]
)


@router.post(
    "/{paper_id}/verify-extraction",
    response_model=VerificationResponse
)
def verify_paper_extraction(
    project_id: int,
    paper_id: int,
    request: VerificationRequest,
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

    # Get latest extraction
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

    if extraction is None:
        raise HTTPException(
            status_code=404,
            detail="No extraction found for this paper"
        )

    # Validate requested field
    allowed_fields = {
        "population",
        "intervention",
        "comparison",
        "methodology",
        "dataset",
        "sample_size",
        "results",
        "metrics",
        "limitations",
        "conclusion"
    }

    if request.field_name not in allowed_fields:
        raise HTTPException(
            status_code=400,
            detail="Invalid extraction field"
        )

    # Evidence stored during extraction
    evidence_text = extraction.evidence_text

    if not evidence_text:
        raise HTTPException(
            status_code=404,
            detail="No evidence available for this extraction"
        )

    # Verify with AI
    try:
        verification = verify_extraction(
            extracted_field=request.field_name,
            extracted_value=request.extracted_value,
            evidence_text=evidence_text
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evidence verification failed: {str(e)}"
        )

    return {
        "field_name": request.field_name,
        "extracted_value": request.extracted_value,
        "verified": verification.get("verified", False),
        "confidence": verification.get("confidence", 0),
        "explanation": verification.get(
            "explanation",
            ""
        )
    }