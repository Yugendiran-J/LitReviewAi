from sqlalchemy.orm import Session

from ..models import PaperChunk
from .chunk_service import split_text_into_chunks


def create_paper_chunks(
    db: Session,
    paper_id: int,
    pages: list[dict]
):

    # Remove old chunks first
    db.query(PaperChunk).filter(
        PaperChunk.paper_id == paper_id
    ).delete()

    chunk_index = 1

    for page in pages:

        page_number = page["page_number"]
        page_text = page["text"]

        chunks = split_text_into_chunks(
            page_text
        )

        for chunk in chunks:

            paper_chunk = PaperChunk(
                paper_id=paper_id,
                chunk_index=chunk_index,
                page_number=page_number,
                chunk_text=chunk
            )

            db.add(paper_chunk)

            chunk_index += 1

    db.commit()