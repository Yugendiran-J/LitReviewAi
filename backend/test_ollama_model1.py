from app.services.discovery_service import generate_search_queries


print("=" * 60)
print("LITREVIEWAI - OLLAMA MODEL 1 TEST")
print("=" * 60)

try:

    result = generate_search_queries(
        research_topic="Artificial Intelligence in Healthcare",
        research_question=(
            "How is artificial intelligence used "
            "to improve healthcare?"
        ),
        population="Healthcare patients",
        intervention="Artificial Intelligence",
        comparison="Traditional healthcare methods",
        outcome="Improved healthcare outcomes",
        study_type="Systematic Review"
    )

    print("\nModel 1 Result:")
    print("-" * 60)

    print(f"AI Model: {result['ai_model']}")
    print(f"Total Queries: {result['total_queries']}")

    print("\nGenerated PubMed Queries:")

    for index, query in enumerate(
        result["queries"],
        start=1
    ):
        print(f"{index}. {query}")

    print("\n" + "=" * 60)
    print("MODEL 1 TEST SUCCESSFUL")
    print("=" * 60)

except Exception as error:

    print("\n" + "=" * 60)
    print("MODEL 1 TEST FAILED")
    print("=" * 60)

    print(type(error).__name__)
    print(error)