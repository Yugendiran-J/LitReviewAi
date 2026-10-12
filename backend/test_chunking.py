from app.database import SessionLocal
from app.models import Paper
from app.services.chunk_service import split_text_into_chunks


db = SessionLocal()

try:
    paper = db.query(Paper).first()

    if paper is None:
        print("No paper found.")
    elif not paper.full_text:
        print("No full text found.")
    else:

        chunks = split_text_into_chunks(
            paper.full_text
        )

        print("Paper ID:", paper.id)
        print("Title:", paper.title)
        print("Full text length:", len(paper.full_text))
        print("Number of chunks:", len(chunks))

        for index, chunk in enumerate(chunks[:3], start=1):

            print("\n-------------------------")
            print("CHUNK", index)
            print("-------------------------")

            print(chunk[:500])

finally:
    db.close()