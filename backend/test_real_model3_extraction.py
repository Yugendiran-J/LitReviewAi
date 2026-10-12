from app.database import SessionLocal

from app.services.model3_processing_service import (
    process_model3_extraction
)


# ============================================================
# USE THE SAME VALUES FROM STEP 8
# ============================================================

PROJECT_ID = 2
PAPER_ID = 133


db = SessionLocal()


try:

    print("=" * 70)
    print("LITREVIEWAI - REAL MODEL 3 EXTRACTION")
    print("=" * 70)

    print()
    print(f"Project ID: {PROJECT_ID}")
    print(f"Paper ID:   {PAPER_ID}")

    print()
    print("Starting:")
    print("FAISS → RAG → Ollama Model 3 → MySQL")

    # --------------------------------------------------------
    # Run Model 3 extraction
    # --------------------------------------------------------

    result = process_model3_extraction(
        db=db,
        project_id=PROJECT_ID,
        paper_id=PAPER_ID
    )

    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("MODEL 3 EXTRACTION SUCCESSFUL")
    print("=" * 70)

    print()
    print("Paper ID:")
    print(result["paper_id"])

    print()
    print("Title:")
    print(result["title"])

    print()
    print("Retrieved FAISS chunks:")
    print(result["retrieved_chunks"])

    print()
    print("Extraction ID:")
    print(result["extraction_id"])

    print()
    print("Confidence:")
    print(result["confidence"])

    # --------------------------------------------------------
    # Extracted information
    # --------------------------------------------------------

    extraction = result["extraction"]

    print()
    print("=" * 70)
    print("EXTRACTED RESEARCH INFORMATION")
    print("=" * 70)

    print()
    print("Population:")
    print(extraction.get(
        "population",
        "Not reported"
    ))

    print()
    print("Intervention:")
    print(extraction.get(
        "intervention",
        "Not reported"
    ))

    print()
    print("Comparison:")
    print(extraction.get(
        "comparison",
        "Not reported"
    ))

    print()
    print("Methodology:")
    print(extraction.get(
        "methodology",
        "Not reported"
    ))

    print()
    print("Dataset:")
    print(extraction.get(
        "dataset",
        "Not reported"
    ))

    print()
    print("Sample Size:")
    print(extraction.get(
        "sample_size",
        "Not reported"
    ))

    print()
    print("Results:")
    print(extraction.get(
        "results",
        "Not reported"
    ))

    print()
    print("Metrics:")
    print(extraction.get(
        "metrics",
        "Not reported"
    ))

    print()
    print("Limitations:")
    print(extraction.get(
        "limitations",
        "Not reported"
    ))

    print()
    print("Conclusion:")
    print(extraction.get(
        "conclusion",
        "Not reported"
    ))

    print()
    print("Evidence items:")
    print(
        len(
            extraction.get(
                "evidence",
                []
            )
        )
    )

    print()
    print("=" * 70)
    print("REAL MODEL 3 EXTRACTION TEST COMPLETED")
    print("=" * 70)


except Exception as error:

    db.rollback()

    print()
    print("=" * 70)
    print("MODEL 3 EXTRACTION FAILED")
    print("=" * 70)

    print(
        type(error).__name__
    )

    print(error)


finally:

    db.close()