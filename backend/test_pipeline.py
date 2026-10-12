from app.database import SessionLocal
from app.services.pipeline_service import run_literature_pipeline


PROJECT_ID = 2

KEYWORD = "artificial intelligence systematic literature review"

DOMAIN = "Artificial Intelligence and Computer Science"

POPULATION = "Researchers conducting systematic literature reviews"

INTERVENTION = "Artificial intelligence and large language models"

COMPARISON = "Traditional systematic literature review methods"

OUTCOME = "Improved efficiency, accuracy, screening, extraction, and review quality"

STUDY_TYPE = "Research studies evaluating AI-assisted systematic literature reviews"


db = SessionLocal()

try:

    result = run_literature_pipeline(
        db=db,
        project_id=PROJECT_ID,
        keyword=KEYWORD,
        domain=DOMAIN,
        population=POPULATION,
        intervention=INTERVENTION,
        comparison=COMPARISON,
        outcome=OUTCOME,
        study_type=STUDY_TYPE,
        max_queries=5,
        max_results_per_query=10
    )

    print("\n====================================")
    print("PIPELINE COMPLETED")
    print("====================================")

    print("Project ID:", result["project_id"])

    print(
        "Generated Queries:",
        result["model1"]["query_count"]
    )

    print(
        "Candidates:",
        result["candidate_collection"]["total_candidates"]
    )

    print(
        "Abstracts Updated:",
        result["abstract_retrieval"]["updated"]
    )

    print(
        "Model 2 Included:",
        result["model2"]["included"]
    )

    print(
        "Model 2 Uncertain:",
        result["model2"]["uncertain"]
    )

    print(
        "Model 2 Excluded:",
        result["model2"]["excluded"]
    )

finally:
    db.close()