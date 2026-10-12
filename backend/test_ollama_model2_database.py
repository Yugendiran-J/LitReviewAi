from app.database import SessionLocal
from app.services.screening_model2_service import (
    screen_project_papers
)


# IMPORTANT:
# Replace this with an EXISTING project ID
# from your LitReviewAI database.
PROJECT_ID = 3


db = SessionLocal()


try:

    print("=" * 60)
    print("LITREVIEWAI - OLLAMA MODEL 2 DATABASE TEST")
    print("=" * 60)

    # Get papers belonging to this project
    from app.models import Paper

    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == PROJECT_ID
        )
        .limit(3)
        .all()
    )

    if not papers:
        raise ValueError(
            "No papers found for this project."
        )

    paper_ids = [
        paper.id
        for paper in papers
    ]

    print(
        f"\nTesting with paper IDs: "
        f"{paper_ids}"
    )

    result = screen_project_papers(
        db=db,
        project_id=PROJECT_ID,

        population="Healthcare patients",

        intervention="Artificial Intelligence",

        comparison="Traditional healthcare methods",

        outcome="Improved healthcare outcomes",

        study_type="Systematic Review",

        paper_ids=paper_ids
    )

    print("\nScreening Result:")
    print("-" * 60)

    print(
        f"Total Screened: "
        f"{result['total_screened']}"
    )

    print(
        f"Ollama Calls: "
        f"{result['ai_calls']}"
    )

    print(
        f"Cached Results: "
        f"{result['cached_results']}"
    )

    print("\nPapers:")

    for paper in result["results"]:

        print(
            f"\nPaper ID: "
            f"{paper['paper_id']}"
        )

        print(
            f"Decision: "
            f"{paper['decision']}"
        )

        print(
            f"Confidence: "
            f"{paper['confidence']}"
        )

        print(
            f"Reason: "
            f"{paper['reason']}"
        )

    print("\n" + "=" * 60)
    print("MODEL 2 DATABASE TEST SUCCESSFUL")
    print("=" * 60)


except Exception as error:

    db.rollback()

    print("\n" + "=" * 60)
    print("MODEL 2 DATABASE TEST FAILED")
    print("=" * 60)

    print(
        type(error).__name__
    )

    print(error)


finally:

    db.close()