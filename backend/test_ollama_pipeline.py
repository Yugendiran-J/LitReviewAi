from app.database import SessionLocal

from app.ai.pipeline_service import (
    run_literature_pipeline
)


# ------------------------------------------------------------
# IMPORTANT
# Replace this with an EXISTING project ID.
# ------------------------------------------------------------

PROJECT_ID = 7


db = SessionLocal()


try:

    print("=" * 70)
    print("LITREVIEWAI - OLLAMA MODEL 1 + MODEL 2 PIPELINE TEST")
    print("=" * 70)

    result = run_literature_pipeline(

        db=db,

        project_id=PROJECT_ID,

        research_topic=(
            "Artificial Intelligence in Healthcare"
        ),

        research_question=(
            "How is artificial intelligence used "
            "to improve healthcare?"
        ),

        population=(
            "Healthcare patients"
        ),

        intervention=(
            "Artificial Intelligence"
        ),

        comparison=(
            "Traditional healthcare methods"
        ),

        outcome=(
            "Improved healthcare outcomes"
        ),

        study_type=(
            "Systematic Review"
        ),

        keywords=[
            "artificial intelligence",
            "healthcare",
            "machine learning",
            "systematic review"
        ]
    )

    print()
    print("=" * 70)
    print("PIPELINE RESULT")
    print("=" * 70)

    print(
        f"Candidate papers: "
        f"{result['candidate_collection']['total_candidates']}"
    )

    print(
        f"Prefilter selected: "
        f"{result['prefilter']['total_selected']}"
    )

    print(
        f"Model 2 screened: "
        f"{result['model2']['total_screened']}"
    )

    print(
        f"Included: "
        f"{result['included_count']}"
    )

    print(
        f"Uncertain: "
        f"{result['uncertain_count']}"
    )

    print(
        f"Excluded: "
        f"{result['excluded_count']}"
    )

    print(
        f"Shortlist: "
        f"{result['shortlist_count']}"
    )

    print()
    print("=" * 70)
    print("OLLAMA MODEL 1 + MODEL 2 PIPELINE TEST SUCCESSFUL")
    print("=" * 70)


except Exception as error:

    db.rollback()

    print()
    print("=" * 70)
    print("PIPELINE TEST FAILED")
    print("=" * 70)

    print(
        type(error).__name__
    )

    print(error)


finally:

    db.close()