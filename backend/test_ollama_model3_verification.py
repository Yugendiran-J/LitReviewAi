from app.ai.verification_model3_service import (
    verify_evidence
)


print("=" * 70)
print("LITREVIEWAI - OLLAMA MODEL 3 VERIFICATION TEST")
print("=" * 70)


claim = (
    "The study found that artificial intelligence "
    "improved diagnostic performance."
)


test_evidence = [
    {
        "page_number": 3,
        "chunk_id": "test-1",
        "chunk_text": (
            "The included studies evaluated machine learning "
            "methods for clinical decision support. The reported "
            "outcomes included improved diagnostic performance."
        )
    },
    {
        "page_number": 4,
        "chunk_id": "test-2",
        "chunk_text": (
            "Several studies reported improvements in diagnostic "
            "accuracy following the use of machine learning."
        )
    }
]


try:

    result = verify_evidence(
        claim=claim,
        evidence_chunks=test_evidence
    )

    print("\nVerification Result:")
    print("-" * 70)

    print(
        "Verification:",
        result["verification"]
    )

    print(
        "Confidence:",
        result["confidence"]
    )

    print(
        "Explanation:",
        result["explanation"]
    )

    print(
        "Evidence Count:",
        len(result["evidence"])
    )

    print("\n" + "=" * 70)
    print("MODEL 3 VERIFICATION TEST SUCCESSFUL")
    print("=" * 70)


except Exception as error:

    print("\n" + "=" * 70)
    print("MODEL 3 VERIFICATION TEST FAILED")
    print("=" * 70)

    print(
        type(error).__name__
    )

    print(error)