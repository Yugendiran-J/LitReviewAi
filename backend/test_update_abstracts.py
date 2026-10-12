from app.database import SessionLocal
from app.services.candidate_service import (
    update_candidate_abstracts
)


PROJECT_ID = 2


db = SessionLocal()

try:

    print("\nUPDATING CANDIDATE ABSTRACTS")
    print("============================")

    result = update_candidate_abstracts(
        db=db,
        project_id=PROJECT_ID
    )

    print("\nRESULT")
    print("======")

    print(
        "Total papers:",
        result["total_papers"]
    )

    print(
        "Abstracts updated:",
        result["updated"]
    )

    print(
        "Missing abstracts:",
        result["missing_abstract"]
    )

finally:

    db.close()