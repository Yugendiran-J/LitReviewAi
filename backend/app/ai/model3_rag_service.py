from ..services.vector_service import search_vector_index
from .verification_model3_service import verify_evidence


def verify_claim_with_rag(
    paper_id: int,
    claim: str,
    top_k: int = 5
):
    """
    Retrieve relevant evidence from FAISS and
    send it to AI Model 3 for verification.
    """

    # --------------------------------------------------------
    # 1. Validate claim
    # --------------------------------------------------------

    if not claim or not claim.strip():
        raise ValueError(
            "Claim cannot be empty"
        )

    # --------------------------------------------------------
    # 2. Search FAISS
    # --------------------------------------------------------

    retrieved_chunks = search_vector_index(
        paper_id=paper_id,
        query=claim,
        top_k=top_k
    )

    if not retrieved_chunks:
        raise ValueError(
            "No relevant evidence found in FAISS"
        )

    # --------------------------------------------------------
    # 3. Send retrieved evidence to Model 3
    # --------------------------------------------------------

    verification_result = verify_evidence(
        claim=claim,
        evidence_chunks=retrieved_chunks
    )

    # --------------------------------------------------------
    # 4. Return complete result
    # --------------------------------------------------------

    return {
        "paper_id": paper_id,
        "claim": claim,
        "retrieved_evidence": retrieved_chunks,
        "verification": verification_result
    }