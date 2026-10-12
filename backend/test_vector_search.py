from app.database import SessionLocal
from app.models import PaperChunk
from app.services.vector_service import (
    create_vector_index,
    search_vector_index
)


db = SessionLocal()

try:

    paper_id = 1

    chunks_db = (
        db.query(PaperChunk)
        .filter(
            PaperChunk.paper_id == paper_id
        )
        .order_by(
            PaperChunk.chunk_index.asc()
        )
        .all()
    )

    if not chunks_db:
        print("No chunks found for this paper.")
        print("Run test_paper_chunks.py first.")

    else:

        chunks = []

        for chunk in chunks_db:

            chunks.append({
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "chunk_text": chunk.chunk_text
            })

        # Create FAISS index
        result = create_vector_index(
            project_id=1,
            paper_id=paper_id,
            chunks=chunks
        )

        print("Vector index created:")
        print(result)

        # Test semantic search
        search_results = search_vector_index(
            paper_id=paper_id,
            query="What is the sample size?",
            top_k=3
        )

        print("\nSearch Results:")

        for item in search_results:

            print("\n----------------------")
            print(
                "Page:",
                item["page_number"]
            )

            print(
                "Distance:",
                item["distance"]
            )

            print(
                "Text:",
                item["chunk_text"][:500]
            )

finally:

    db.close()