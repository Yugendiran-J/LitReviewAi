from app.ai.model3_extraction_service import (
    extract_research_data_from_evidence
)


print("=" * 70)
print("LITREVIEWAI - OLLAMA MODEL 3 EXTRACTION TEST")
print("=" * 70)


test_evidence = [
    {
        "page_number": 1,
        "chunk_id": "test-1",
        "chunk_text": (
            "This systematic review investigated the use of "
            "artificial intelligence in healthcare. The review "
            "included 25 studies involving healthcare applications."
        )
    },
    {
        "page_number": 3,
        "chunk_id": "test-2",
        "chunk_text": (
            "The included studies evaluated machine learning "
            "methods for clinical decision support. The reported "
            "outcomes included improved diagnostic performance."
        )
    }
]


try:

    result = extract_research_data_from_evidence(
        title=(
            "Artificial Intelligence Applications "
            "in Healthcare: A Systematic Review"
        ),
        evidence_chunks=test_evidence
    )

    print("\nExtraction Result:")
    print("-" * 70)

    print(
        "Population:",
        result["population"]
    )

    print(
        "Intervention:",
        result["intervention"]
    )

    print(
        "Comparison:",
        result["comparison"]
    )

    print(
        "Methodology:",
        result["methodology"]
    )

    print(
        "Dataset:",
        result["dataset"]
    )

    print(
        "Sample Size:",
        result["sample_size"]
    )

    print(
        "Results:",
        result["results"]
    )

    print(
        "Metrics:",
        result["metrics"]
    )

    print(
        "Limitations:",
        result["limitations"]
    )

    print(
        "Conclusion:",
        result["conclusion"]
    )

    print(
        "Confidence:",
        result["confidence"]
    )

    print(
        "Evidence Count:",
        len(result["evidence"])
    )

    print("\n" + "=" * 70)
    print("MODEL 3 EXTRACTION TEST SUCCESSFUL")
    print("=" * 70)


except Exception as error:

    print("\n" + "=" * 70)
    print("MODEL 3 EXTRACTION TEST FAILED")
    print("=" * 70)

    print(
        type(error).__name__
    )

    print(error)