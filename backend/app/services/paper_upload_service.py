import os

from sqlalchemy.orm import Session

from ..models import Paper
from .fulltext_pipeline_service import process_paper_fulltext


UPLOAD_DIRECTORY = "documents/papers"


def save_uploaded_pdf(
    db: Session,
    project_id: int,
    paper_id: int,
    file
):
    # ---------------------------------
    # Check paper
    # ---------------------------------

    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.project_id == project_id
        )
        .first()
    )

    if not paper:
        raise ValueError(
            "Paper not found for this project"
        )

    # ---------------------------------
    # Validate filename
    # ---------------------------------

    filename = file.filename or ""

    if not filename.lower().endswith(".pdf"):
        raise ValueError(
            "Only PDF files are allowed"
        )

    # ---------------------------------
    # Create directory
    # ---------------------------------

    paper_directory = os.path.join(
        UPLOAD_DIRECTORY,
        str(project_id)
    )

    os.makedirs(
        paper_directory,
        exist_ok=True
    )

    # ---------------------------------
    # Create safe filename
    # ---------------------------------

    filename = f"paper_{paper_id}.pdf"

    pdf_path = os.path.join(
        paper_directory,
        filename
    )

    # ---------------------------------
    # Save PDF
    # ---------------------------------

    with open(pdf_path, "wb") as output_file:

        while True:

            chunk = file.file.read(1024 * 1024)

            if not chunk:
                break

            output_file.write(chunk)

    # ---------------------------------
    # Full-text processing
    # ---------------------------------

    result = process_paper_fulltext(
        db=db,
        project_id=project_id,
        paper_id=paper_id,
        pdf_path=pdf_path
    )

    return result