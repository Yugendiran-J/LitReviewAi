from app.database import SessionLocal
from app.models import Paper
from app.services.screening_model2_service import screen_candidate_paper


PROJECT_ID = 3
PAPER_ID = 618

POPULATION = "researchers and research studies"
INTERVENTION = "artificial intelligence and large language models"
COMPARISON = "traditional systematic literature review methods"
OUTCOME = "screening accuracy and literature review efficiency"
STUDY_TYPE = "systematic review"


print("=" * 70)
print("SINGLE PAPER MODEL 2 TEST")
print("=" * 70)


db = SessionLocal()

try:
    paper = db.query(Paper).filter(
        Paper.id == PAPER_ID,
        Paper.project_id == PROJECT_ID
    ).first()

    if not paper:
        raise ValueError(
            f"Paper {PAPER_ID} was not found in project {PROJECT_ID}"
        )

    print("\nPaper found:")
    print(f"ID: {paper.id}")
    print(f"Title: {paper.title}")

    result = screen_candidate_paper(
        title=paper.title,
        abstract=paper.abstract or "",
        population=POPULATION,
        intervention=INTERVENTION,
        comparison=COMPARISON,
        outcome=OUTCOME,
        study_type=STUDY_TYPE
    )

    print("\n")
    print("=" * 70)
    print("MODEL 2 TEST SUCCESSFUL")
    print("=" * 70)

    print("\nResult:")
    print(result)

except Exception as error:
    print("\n")
    print("=" * 70)
    print("MODEL 2 TEST FAILED")
    print("=" * 70)

    print("\nError:")
    print(error)

    raise

finally:
    db.close()