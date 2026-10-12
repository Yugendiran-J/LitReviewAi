from app.ai.screening_model2_service import screen_candidate_paper


result = screen_candidate_paper(
    title="Artificial Intelligence for Systematic Literature Reviews",
    abstract="""
    This study investigates the use of artificial intelligence and
    large language models to support systematic literature review
    processes including literature screening and data extraction.
    """,
    population="Researchers conducting systematic literature reviews",
    intervention="Artificial intelligence based literature review assistance",
    comparison="Traditional manual systematic literature review",
    outcome="Improved screening efficiency and review quality",
    study_type="Research study"
)


print("\nAI MODEL 2 RESULT")
print("=================")

print("Decision:")
print(result["decision"])

print("\nConfidence:")
print(result["confidence"])

print("\nReason:")
print(result["reason"])

print("\nPICOS Analysis:")

for criterion, value in result["picos_analysis"].items():
    print(f"{criterion}: {value}")