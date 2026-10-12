import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ResearchProject, Paper, User
from ..dependencies import get_current_user
from ..services.pdf_service import extract_text_from_pdf


router = APIRouter(
    prefix="/projects/{project_id}/upload",
    tags=["PDF Upload"]
)


@router.post("/pdf/{paper_id}")
def upload_pdf(
    project_id: int,
    paper_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------
    # 1. Check project ownership
    # -----------------------------------------
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

    # -----------------------------------------
    # 2. Check paper
    # -----------------------------------------
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

    # -----------------------------------------
    # 3. Validate file
    # -----------------------------------------
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # -----------------------------------------
    # 4. Create project upload directory
    # -----------------------------------------
    upload_directory = os.path.join(
        "documents",
        f"project_{project_id}"
    )

    os.makedirs(
        upload_directory,
        exist_ok=True
    )

    # -----------------------------------------
    # 5. Create safe filename
    # -----------------------------------------
    filename = os.path.basename(file.filename)

    file_path = os.path.join(
        upload_directory,
        filename
    )

    # -----------------------------------------
    # 6. Save PDF
    # -----------------------------------------
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save PDF: {str(e)}"
        )

    # -----------------------------------------
    # 7. Save PDF path in database
    # -----------------------------------------
    # -----------------------------------------
    # 8. Extract text from PDF
    # -----------------------------------------
    try:
        extracted_text = extract_text_from_pdf(
            file_path
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"PDF text extraction failed: {str(e)}"
        )

    # -----------------------------------------
    # 9. Check extracted text
    # -----------------------------------------
    if not extracted_text.strip():
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found in the PDF. "
                "The PDF may be scanned or image-based."
            )
        )

    # -----------------------------------------
    # 10. Save extracted text and database changes
    # -----------------------------------------
    paper.pdf_path = file_path
    paper.full_text = extracted_text
    db.commit()
    db.refresh(paper)

    # -----------------------------------------
    # 11. Return result
    # -----------------------------------------
    return {
        "message": "PDF uploaded and text extracted successfully",
        "paper_id": paper.id,
        "filename": filename,
        "pdf_path": file_path,
        "text_length": len(extracted_text),
        "text_preview": extracted_text[:2000]
    }