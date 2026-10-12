from app.database import SessionLocal

from app.ai.model3_extraction_rag_service import (
    extract_paper_data_with_rag
)

from app.services.extraction_storage_service import (
    save_extraction_result
)


PROJECT_ID = 2
PAPER_ID = 15

TITLE = (
    "Artificial Intelligence for Systematic "
    "Literature Review"
)

EXTRACTION_QUERY = """
Extract the study methodology, population,
intervention, comparison, dataset, sample size,
results, metrics, limitations and conclusion.
"""


db = SessionLocal()

try:

    print("\nMODEL 3 EXTRACTION")
    print("==================")

    result = extract_paper_data_with_rag(
        paper_id=PAPER_ID,
        title=TITLE,
        extraction_query=EXTRACTION_QUERY,
        top_k=8
    )

    extraction = result["extraction"]

    print("\nSAVING TO MYSQL")
    print("================")

    saved = save_extraction_result(
        db=db,
        project_id=PROJECT_ID,
        paper_id=PAPER_ID,
        extraction=extraction
    )

    print("\nSUCCESS")
    print("=======")

    print(
        "Extraction ID:",
        saved.id
    )

    print(
        "Paper ID:",
        saved.paper_id
    )

    print(
        "Confidence:",
        saved.extraction_confidence
    )

    print(
        "Evidence Location:",
        saved.evidence_location
    )

finally:

    db.close()