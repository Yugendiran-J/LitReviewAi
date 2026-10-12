from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    Paper,
    ExtractedData,
    HumanFeedback,
    User
)
from ..dependencies import get_current_user
from ..schemas import (
    ExtractionValidationRequest,
    ExtractionValidationResponse
)


router = APIRouter(
    prefix="/projects/{project_id}/papers",
    tags=["Human Validation"]
)


@router.post(
    "/{paper_id}/validate-extraction",
    response_model=ExtractionValidationResponse
)
def validate_extraction(
    project_id: int,
    paper_id: int,
    request: ExtractionValidationRequest,
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
    # 2. Check paper
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
    # 3. Get latest extraction
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

    if extraction is None:
        raise HTTPException(
            status_code=404,
            detail="No extraction found"
        )

    # --------------------------------
    # 4. Validate field
    # --------------------------------
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

    # --------------------------------
    # 5. Validate status
    # --------------------------------
    if request.status not in {
        "accepted",
        "corrected"
    }:
        raise HTTPException(
            status_code=400,
            detail="Status must be accepted or corrected"
        )

    # --------------------------------
    # 6. Get current field value
    # --------------------------------
    current_value = getattr(
        extraction,
        request.field_name
    )

    # --------------------------------
    # 7. Check original value
    # --------------------------------
    if current_value != request.original_value:
        raise HTTPException(
            status_code=409,
            detail="Original value does not match the latest extraction"
        )

    # --------------------------------
    # 8. Determine final value
    # --------------------------------
    if request.status == "corrected":

        if not request.corrected_value:
            raise HTTPException(
                status_code=400,
                detail="corrected_value is required"
            )

        final_value = request.corrected_value

        setattr(
            extraction,
            request.field_name,
            final_value
        )

    else:
        final_value = current_value

    # --------------------------------
    # 9. Store human feedback
    # --------------------------------
    feedback = HumanFeedback(
        paper_id=paper_id,
        original_decision=request.original_value,
        corrected_decision=final_value,
        feedback_text=request.feedback,
        reviewer_name=request.reviewer_name
    )

    db.add(feedback)

    # --------------------------------
    # 10. Save changes
    # --------------------------------
    db.commit()
    db.refresh(extraction)

    return {
        "message": "Extraction validation saved successfully",
        "extraction_id": extraction.id,
        "field_name": request.field_name,
        "status": request.status,
        "final_value": final_value
    }