from app.database import SessionLocal

from app.services.fulltext_pipeline_service import (
    process_paper_fulltext
)


PROJECT_ID = 2
PAPER_ID = 15


PDF_PATH = "documents/test.pdf"


db = SessionLocal()

try:

    print("\nFULL-TEXT PROCESSING PIPELINE")
    print("==============================")

    result = process_paper_fulltext(
        db=db,
        project_id=PROJECT_ID,
        paper_id=PAPER_ID,
        pdf_path=PDF_PATH
    )

    print("\nPROCESSING RESULT")
    print("=================")

    print(
        "Project ID:",
        result["project_id"]
    )

    print(
        "Paper ID:",
        result["paper_id"]
    )

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

finally:

    db.close()