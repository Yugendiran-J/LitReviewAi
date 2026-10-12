from app.database import SessionLocal
from app.services.screening_model2_service import screen_project_papers


PROJECT_ID = 3

POPULATION = "researchers and research studies"
INTERVENTION = "artificial intelligence and large language models"
COMPARISON = "traditional systematic literature review methods"
OUTCOME = "screening accuracy and literature review efficiency"
STUDY_TYPE = "systematic review"


print("=" * 70)
print("MODEL 2 MULTI-PAPER TEST")
print("=" * 70)

db = SessionLocal()

try:
    result = screen_project_papers(
        db=db,
        project_id=PROJECT_ID,
        population=POPULATION,
        intervention=INTERVENTION,
        comparison=COMPARISON,
        outcome=OUTCOME,
        study_type=STUDY_TYPE,
        paper_ids=[618, 619, 620]
    )

    print("\n")
    print("=" * 70)
    print("MODEL 2 PIPELINE TEST SUCCESSFUL")
    print("=" * 70)

    print("\nResult:")
    print(result)

except Exception as error:
    print("\n")
    print("=" * 70)
    print("MODEL 2 PIPELINE TEST FAILED")
    print("=" * 70)

    print("\nError:")
    print(error)

    raise

finally:
    db.close()