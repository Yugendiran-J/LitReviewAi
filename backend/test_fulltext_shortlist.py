from app.database import SessionLocal
from app.services.fulltext_shortlist_service import (
    get_fulltext_candidates
)


PROJECT_ID = 2

db = SessionLocal()

try:

    result = get_fulltext_candidates(
        db=db,
        project_id=PROJECT_ID
    )

    print("\n====================================")
    print("FULL-TEXT CANDIDATE SHORTLIST")
    print("====================================")

    print(
        "Included papers:",
        result["included_count"]
    )

    print(
        "Uncertain papers:",
        result["uncertain_count"]
    )

    print("\n------------------------------------")
    print("PAPERS MOVING TO FULL-TEXT STAGE")
    print("------------------------------------")

    for paper in result["included"]:

        print(
            f'\nPaper ID: {paper["paper_id"]}'
        )

        print(
            f'Title: {paper["title"]}'
        )

        print(
            f'Confidence: {paper["confidence"]}'
        )

        print(
            f'URL: {paper["url"]}'
        )

finally:
    db.close()