from app.database import SessionLocal
from app.models import Paper
from app.services.vector_service import search_vector_index
from app.ai.extraction_service import extract_research_data


db = SessionLocal()

try:
    paper_id = 1

    paper = (
        db.query(Paper)
        .filter(Paper.id == paper_id)
        .first()
    )

    if not paper:
        print("Paper not found.")
    else:
        query = "Extract the sample size, methodology, results, and conclusion."

        print("Searching relevant evidence...")

        retrieved_chunks = search_vector_index(
            paper_id=paper_id,
            query=query,
            top_k=5
        )

        print(f"Retrieved {len(retrieved_chunks)} chunks.")

        print("\nSending evidence to AI...")

        result = extract_research_data(
            title=paper.title,
            query=query,
            retrieved_chunks=retrieved_chunks
        )

        print("\nAI EXTRACTION RESULT")
        print("====================")

        print(result)

finally:
    db.close()