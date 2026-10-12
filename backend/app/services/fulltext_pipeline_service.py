from sqlalchemy.orm import Session

from ..models import Paper, PaperChunk

from .pdf_service import extract_pages_from_pdf
from .chunk_storage_service import create_paper_chunks
from .vector_service import create_vector_index


def process_paper_fulltext(
    db: Session,
    project_id: int,
    paper_id: int,
    pdf_path: str
):
    """
    Complete full-text processing pipeline:

    PDF
      ↓
    Page extraction
      ↓
    MySQL chunks
      ↓
    FAISS vector index
    """

    # --------------------------------------------------------
    # 1. Find the paper
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 2. Extract pages from PDF
    # --------------------------------------------------------

    pages = extract_pages_from_pdf(
        pdf_path
    )

    if not pages:
        raise ValueError(
            "No text could be extracted from PDF"
        )

    # --------------------------------------------------------
    # 3. Save PDF path
    # --------------------------------------------------------

    paper.pdf_path = pdf_path

    # --------------------------------------------------------
    # 4. Create page-aware chunks
    # --------------------------------------------------------

    create_paper_chunks(
        db=db,
        paper_id=paper_id,
        pages=pages
    )

    # --------------------------------------------------------
    # 5. Retrieve chunks from database
    # --------------------------------------------------------

    chunks = (
        db.query(PaperChunk)
        .filter(
            PaperChunk.paper_id == paper_id
        )
        .order_by(
            PaperChunk.chunk_index
        )
        .all()
    )

    if not chunks:
        raise ValueError(
            "No chunks were created"
        )

    # --------------------------------------------------------
    # 6. Convert SQLAlchemy objects to dictionaries
    # --------------------------------------------------------

    chunk_data = []

    for chunk in chunks:

        chunk_data.append(
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "chunk_text": chunk.chunk_text
            }
        )

    # --------------------------------------------------------
    # 7. Create FAISS vector index
    # --------------------------------------------------------

    vector_result = create_vector_index(
        project_id=project_id,
        paper_id=paper_id,
        chunks=chunk_data
    )

    # --------------------------------------------------------
    # 8. Save full text into papers table
    # --------------------------------------------------------

    full_text_parts = []

    for page in pages:

        full_text_parts.append(
            page["text"]
        )

    paper.full_text = "\n".join(
        full_text_parts
    )

    db.commit()

    # --------------------------------------------------------
    # 9. Return processing information
    # --------------------------------------------------------

    return {
        "project_id": project_id,
        "paper_id": paper_id,
        "pdf_path": pdf_path,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
        "vector_index": vector_result
    }