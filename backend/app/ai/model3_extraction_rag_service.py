from ..services.vector_service import (
    search_vector_index
)

from .model3_extraction_service import (
    extract_research_data_from_evidence
)


def extract_paper_data_with_rag(
    paper_id: int,
    title: str,
    extraction_query: str,
    top_k: int = 8
):
    """
    Retrieve relevant full-text evidence using FAISS
    and perform structured extraction using Model 3.
    """

    # --------------------------------------------------------
    # 1. Search FAISS
    # --------------------------------------------------------

    retrieved_chunks = search_vector_index(
        paper_id=paper_id,
        query=extraction_query,
        top_k=top_k
    )

    if not retrieved_chunks:

        raise ValueError(
            "No relevant evidence found"
        )

    # --------------------------------------------------------
    # 2. Extract structured information
    # --------------------------------------------------------

    extraction_result = (
        extract_research_data_from_evidence(
            title=title,
            evidence_chunks=retrieved_chunks
        )
    )

    # --------------------------------------------------------
    # 3. Return complete result
    # --------------------------------------------------------

    return {
        "paper_id": paper_id,
        "title": title,
        "query": extraction_query,
        "retrieved_chunks": retrieved_chunks,
        "extraction": extraction_result
    }