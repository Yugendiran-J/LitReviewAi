from app.ai.model3_rag_service import (
    verify_claim_with_rag
)


PAPER_ID = 15

CLAIM = (
    "The study used artificial intelligence "
    "to improve systematic literature review screening."
)


print("\nMODEL 3 + RAG TEST")
print("===================")

result = verify_claim_with_rag(
    paper_id=PAPER_ID,
    claim=CLAIM,
    top_k=5
)


print("\nCLAIM")
print("=====")

print(result["claim"])


print("\nRETRIEVED EVIDENCE")
print("==================")

for index, chunk in enumerate(
    result["retrieved_evidence"],
    start=1
):

    print(
        f"\nEvidence {index}"
    )

    print(
        "Page:",
        chunk["page_number"]
    )

    print(
        "Chunk ID:",
        chunk["chunk_id"]
    )

    print(
        "Distance:",
        chunk["distance"]
    )

    print(
        "Text:"
    )

    print(
        chunk["chunk_text"][:500]
    )


print("\nMODEL 3 VERIFICATION")
print("====================")

verification = result["verification"]

print(
    "Verification:",
    verification["verification"]
)

print(
    "Confidence:",
    verification["confidence"]
)

print(
    "Explanation:",
    verification["explanation"]
)

print("\nSupporting Evidence:")

for evidence in verification["evidence"]:

    print(
        f"\nPage {evidence['page_number']}:"
    )

    print(
        evidence["evidence_text"]
    )