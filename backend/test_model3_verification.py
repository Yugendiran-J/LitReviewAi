from app.database import SessionLocal

from app.services.model3_verification_service import (
    process_model3_verification
)


PROJECT_ID = 2

# Use the SAME paper ID whose PDF was
# successfully uploaded and processed.

PAPER_ID = 133


CLAIM = """
The study uses artificial intelligence to improve
the efficiency of systematic literature review.
"""


db = SessionLocal()

try:

    print("\n====================================")
    print("MODEL 3 EVIDENCE VERIFICATION")
    print("====================================")

    result = process_model3_verification(
        db=db,
        project_id=PROJECT_ID,
        paper_id=PAPER_ID,
        claim=CLAIM
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
        "\nCLAIM:"
    )

    print(result["claim"])

    verification = result["verification"]

    print(
        "\nVERIFICATION:"
    )

    print(
        "Result:",
        verification.get("verification")
    )

    print(
        "Confidence:",
        verification.get("confidence")
    )

    print(
        "Explanation:",
        verification.get("explanation")
    )

    print(
        "\nEVIDENCE:"
    )

    for evidence in verification.get(
        "evidence",
        []
    ):

        print(
            "\nPage:",
            evidence.get("page_number")
        )

        print(
            "Evidence:",
            evidence.get("evidence_text")
        )
        print(
    "Verification ID:",
    result["verification_id"]
)

finally:

    db.close()