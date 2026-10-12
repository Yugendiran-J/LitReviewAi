from app.database import SessionLocal
from app.models import Paper
from app.services.pdf_service import extract_pages_from_pdf
from app.services.chunk_storage_service import create_paper_chunks


db = SessionLocal()

try:

    paper = db.query(Paper).first()

    if paper is None:
        print("No paper found.")

    elif not paper.pdf_path:
        print("No PDF found for this paper.")

    else:

        pages = extract_pages_from_pdf(
            paper.pdf_path
        )

        print(
            "PDF pages extracted:",
            len(pages)
        )

        create_paper_chunks(
            db,
            paper.id,
            pages
        )

        print(
            "Paper chunks created successfully."
        )

finally:
    db.close()