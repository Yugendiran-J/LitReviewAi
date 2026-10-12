from sqlalchemy.orm import Session

from ..models import Paper
from ..ai.model3_extraction_rag_service import (
    extract_paper_data_with_rag
)
from .extraction_storage_service import (
    save_extraction_result
)


def process_model3_extraction(
    db: Session,
    project_id: int,
    paper_id: int
):
    # -----------------------------------------
    # 1. Find paper
    # -----------------------------------------

    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.project_id == project_id
        )
        .first()
    )

    if not paper:
        raise ValueError(
            "Paper not found for this project"
        )

    # -----------------------------------------
    # 2. Check full text
    # -----------------------------------------

    if not paper.full_text:
        raise ValueError(
            "Full text is not available for this paper"
        )

    # -----------------------------------------
    # 3. Extraction query
    # -----------------------------------------

    extraction_query = """
    Extract the following information from this research paper:

    Population
    Intervention
    Comparison
    Methodology
    Dataset
    Sample Size
    Results
    Metrics
    Limitations
    Conclusion

    Use evidence from the paper's full text.
    """

    # -----------------------------------------
    # 4. Model 3 + FAISS/RAG
    # -----------------------------------------

    result = extract_paper_data_with_rag(
        paper_id=paper_id,
        title=paper.title,
        extraction_query=extraction_query,
        top_k=8
    )

    extraction = result["extraction"]

    # -----------------------------------------
    # 5. Save extraction to MySQL
    # -----------------------------------------

    saved = save_extraction_result(
        db=db,
        project_id=project_id,
        paper_id=paper_id,
        extraction=extraction
    )

    return {
        "paper_id": paper_id,
        "title": paper.title,
        "retrieved_chunks": len(
            result["retrieved_chunks"]
        ),
        "extraction_id": saved.id,
        "confidence": saved.extraction_confidence,
        "extraction": extraction
    }