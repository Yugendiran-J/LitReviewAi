from app.database import SessionLocal

from app.services.fulltext_pipeline_service import (
    process_paper_fulltext
)


# ============================================================
# CHANGE THESE VALUES
# ============================================================

PROJECT_ID = 2
PAPER_ID = 133

# Use the REAL PDF path from your database.
PDF_PATH = r"documents/papers/2/paper_133.pdf"


db = SessionLocal()


try:

    print("=" * 70)
    print("LITREVIEWAI - FULL TEXT + FAISS PROCESSING TEST")
    print("=" * 70)

    print()
    print(f"Project ID : {PROJECT_ID}")
    print(f"Paper ID   : {PAPER_ID}")
    print(f"PDF Path   : {PDF_PATH}")

    print()
    print("Starting full-text processing...")

    result = process_paper_fulltext(
        db=db,
        project_id=PROJECT_ID,
        paper_id=PAPER_ID,
        pdf_path=PDF_PATH
    )

    print()
    print("=" * 70)
    print("FULL-TEXT PROCESSING SUCCESSFUL")
    print("=" * 70)

    print()
    print(
        "Total pages:",
        result["total_pages"]
    )

    print(
        "Total chunks:",
        result["total_chunks"]
    )

    print(
        "Vector index:",
        result["vector_index"]
    )

    print()
    print("=" * 70)
    print("FAISS INDEX CREATED SUCCESSFULLY")
    print("=" * 70)


except Exception as error:

    db.rollback()

    print()
    print("=" * 70)
    print("FULL-TEXT PROCESSING FAILED")
    print("=" * 70)

    print(
        type(error).__name__
    )

    print(error)


finally:

    db.close()