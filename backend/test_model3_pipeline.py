from app.database import SessionLocal

from app.services.model3_processing_service import (
    process_model3_extraction
)


PROJECT_ID = 2

# IMPORTANT:
# Replace this with the paper_id
# whose PDF you uploaded in Step 13.22.

PAPER_ID = 133


db = SessionLocal()

try:

    print("\n====================================")
    print("MODEL 3 RAG EXTRACTION")
    print("====================================")

    result = process_model3_extraction(
        db=db,
        project_id=PROJECT_ID,
        paper_id=PAPER_ID
    )

    print("\nSUCCESS")
    print("====================================")

    print(
        "Paper ID:",
        result["paper_id"]
    )

    print(
        "Title:",
        result["title"]
    )

    print(
        "Retrieved Chunks:",
        result["retrieved_chunks"]
    )

    print(
        "Extraction ID:",
        result["extraction_id"]
    )

    print(
        "Confidence:",
        result["confidence"]
    )

    print("\nEXTRACTED DATA")
    print("------------------------------------")

    extraction = result["extraction"]

    print(
        "Population:",
        extraction["population"]
    )

    print(
        "Intervention:",
        extraction["intervention"]
    )

    print(
        "Comparison:",
        extraction["comparison"]
    )

    print(
        "Methodology:",
        extraction["methodology"]
    )

    print(
        "Dataset:",
        extraction["dataset"]
    )

    print(
        "Sample Size:",
        extraction["sample_size"]
    )

    print(
        "Results:",
        extraction["results"]
    )

    print(
        "Metrics:",
        extraction["metrics"]
    )

    print(
        "Limitations:",
        extraction["limitations"]
    )

    print(
        "Conclusion:",
        extraction["conclusion"]
    )

finally:

    db.close()