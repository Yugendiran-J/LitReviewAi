from app.database import SessionLocal

from app.services.model3_verification_service import (
    process_model3_verification
)


# ============================================================
# USE THE SAME VALUES FROM STEP 9
# ============================================================

PROJECT_ID = 2
PAPER_ID = 133


# ============================================================
# IMPORTANT
# Use a claim that actually appears or is clearly supported
# by the paper.
# ============================================================

CLAIM = (
    "The study achieved an accuracy of 92%."
)


db = SessionLocal()


try:

    print("=" * 70)
    print("LITREVIEWAI - REAL MODEL 3 EVIDENCE VERIFICATION")
    print("=" * 70)

    print()
    print(f"Project ID: {PROJECT_ID}")
    print(f"Paper ID:   {PAPER_ID}")

    print()
    print("Claim:")
    print(CLAIM)

    print()
    print(
        "Starting:"
    )

    print(
        "Claim → FAISS → Evidence → Ollama → MySQL"
    )

    # --------------------------------------------------------
    # Run verification
    # --------------------------------------------------------

    result = process_model3_verification(
        db=db,
        project_id=PROJECT_ID,
        paper_id=PAPER_ID,
        claim=CLAIM
    )

    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("MODEL 3 VERIFICATION SUCCESSFUL")
    print("=" * 70)

    print()
    print("Paper ID:")
    print(result["paper_id"])

    print()
    print("Title:")
    print(result["title"])

    print()
    print("Claim:")
    print(result["claim"])

    verification = result["verification"]

    print()
    print("Verification:")
    print(
        verification.get(
            "verification",
            "Unknown"
        )
    )

    print()
    print("Confidence:")
    print(
        verification.get(
            "confidence",
            0
        )
    )

    print()
    print("Explanation:")
    print(
        verification.get(
            "explanation",
            ""
        )
    )

    evidence = verification.get(
        "evidence",
        []
    )

    print()
    print(
        f"Evidence items: {len(evidence)}"
    )

    # --------------------------------------------------------
    # Display evidence
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("SUPPORTING EVIDENCE")
    print("=" * 70)

    for index, item in enumerate(
        evidence,
        start=1
    ):

        print()
        print(
            f"Evidence {index}"
        )

        print(
            "Page:",
            item.get(
                "page_number",
                "Unknown"
            )
        )

        print(
            "Text:",
            item.get(
                "evidence_text",
                ""
            )
        )

    print()
    print("Verification ID:")
    print(
        result["verification_id"]
    )

    print()
    print("=" * 70)
    print("REAL MODEL 3 VERIFICATION TEST COMPLETED")
    print("=" * 70)


except Exception as error:

    db.rollback()

    print()
    print("=" * 70)
    print("MODEL 3 VERIFICATION FAILED")
    print("=" * 70)

    print(
        type(error).__name__
    )

    print(error)


finally:

    db.close()