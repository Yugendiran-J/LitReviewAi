from app.database import SessionLocal
from app.ai.screening_model2_service import (
    screen_project_papers
)


PROJECT_ID = 2


db = SessionLocal()

try:

    print("\nAI MODEL 2 — BATCH SCREENING")
    print("============================")

    results = screen_project_papers(
        db=db,
        project_id=PROJECT_ID,

        population=(
            "Researchers conducting "
            "systematic literature reviews"
        ),

        intervention=(
            "Artificial intelligence based "
            "literature review assistance"
        ),

        comparison=(
            "Traditional manual systematic "
            "literature review"
        ),

        outcome=(
            "Improved screening efficiency "
            "and review quality"
        ),

        study_type=(
            "Research study"
        )
    )

    print("\nSCREENING SUMMARY")
    print("=================")

    include_count = 0
    exclude_count = 0
    uncertain_count = 0

    for result in results:

        print("\nPaper:")
        print(result["title"])

        print("Decision:")
        print(result["decision"])

        print("Confidence:")
        print(result["confidence"])

        if result["decision"] == "Include":
            include_count += 1

        elif result["decision"] == "Exclude":
            exclude_count += 1

        else:
            uncertain_count += 1

    print("\n=================")
    print("TOTAL:", len(results))
    print("INCLUDE:", include_count)
    print("EXCLUDE:", exclude_count)
    print("UNCERTAIN:", uncertain_count)

finally:

    db.close()