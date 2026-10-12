from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ResearchProject, Paper, ExtractedData, User
from ..dependencies import get_current_user
from ..schemas import ExtractionRequest, ExtractionResponse

from ..services.vector_service import search_vector_index
from ..ai.extraction_service import extract_research_data


router = APIRouter(
    prefix="/projects/{project_id}/papers",
    tags=["AI Extraction"]
)


@router.post(
    "/{paper_id}/extract",
    response_model=ExtractionResponse
)
def extract_paper_data(
    project_id: int,
    paper_id: int,
    request: ExtractionRequest,
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
    # 3. Validate query
    # --------------------------------
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Extraction query cannot be empty"
        )

    if request.top_k < 1:
        raise HTTPException(
            status_code=400,
            detail="top_k must be at least 1"
        )

    # --------------------------------
    # 4. Retrieve relevant chunks
    # --------------------------------
    try:
        retrieved_chunks = search_vector_index(
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
            detail=f"Vector search failed: {str(e)}"
        )

    if not retrieved_chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant evidence found in the paper"
        )

    # --------------------------------
    # 5. Send evidence to AI
    # --------------------------------
    try:
        extracted = extract_research_data(
            title=paper.title,
            query=request.query,
            retrieved_chunks=retrieved_chunks
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI extraction failed: {str(e)}"
        )

    # --------------------------------
    # 6. Prepare evidence
    # --------------------------------
    evidence_items = extracted.get("evidence", [])

    evidence_text = "\n\n".join(
        item.get("evidence_text", "")
        for item in evidence_items
    )

    evidence_location = ", ".join(
        f"Page {item.get('page_number')}"
        for item in evidence_items
        if item.get("page_number") is not None
    )

    confidence = extracted.get("confidence")

    # --------------------------------
    # 7. Save extraction to database
    # --------------------------------
    extracted_data = ExtractedData(
        paper_id=paper_id,
        population=extracted.get("population"),
        intervention=extracted.get("intervention"),
        comparison=extracted.get("comparison"),
        methodology=extracted.get("methodology"),
        dataset=extracted.get("dataset"),
        sample_size=extracted.get("sample_size"),
        results=extracted.get("results"),
        metrics=extracted.get("metrics"),
        limitations=extracted.get("limitations"),
        conclusion=extracted.get("conclusion"),
        evidence_text=evidence_text,
        evidence_location=evidence_location,
        extraction_confidence=str(confidence)
        if confidence is not None
        else None
    )

    db.add(extracted_data)
    db.commit()
    db.refresh(extracted_data)

    return extracted_data