from app.ai.verification_model3_service import (
    verify_evidence
)


claim = (
    "The study used artificial intelligence "
    "to assist systematic literature review screening."
)


evidence_chunks = [
    {
        "chunk_id": 101,
        "page_number": 3,
        "chunk_text": """
        The proposed system uses artificial intelligence
        to assist researchers in screening scientific
        literature for systematic reviews.
        """
    },
    {
        "chunk_id": 102,
        "page_number": 4,
        "chunk_text": """
        The AI-assisted screening process evaluates
        research abstracts according to predefined
        inclusion and exclusion criteria.
        """
    }
]


print("\nAI MODEL 3 — EVIDENCE VERIFICATION")
print("====================================")


result = verify_evidence(
    claim=claim,
    evidence_chunks=evidence_chunks
)


print("\nVerification:")
print(result["verification"])


print("\nConfidence:")
print(result["confidence"])


print("\nExplanation:")
print(result["explanation"])


print("\nEvidence:")

for evidence in result["evidence"]:

    print(
        f"\nPage {evidence['page_number']}:"
    )

    print(
        evidence["evidence_text"]
    )