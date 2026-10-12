from app.ai.discovery_service import generate_search_queries


result = generate_search_queries(
    keyword="AI-powered systematic literature review",
    domain="Computer Science",
    max_queries=5
)

print("\nAI MODEL 1 RESULT")
print("=================")

print("Research Topic:")
print(result["research_topic"])

print("\nGenerated Queries:")

for index, query in enumerate(result["queries"], start=1):
    print(f"{index}. {query}")