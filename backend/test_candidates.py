from app.ai.discovery_service import generate_search_queries
from app.services.candidate_service import collect_candidate_papers


print("\nSTEP 1: GENERATING SEARCH QUERIES")
print("===================================")

query_result = generate_search_queries(
    keyword="AI-powered systematic literature review",
    domain="Computer Science",
    max_queries=5
)

queries = query_result["queries"]

for index, query in enumerate(queries, start=1):
    print(f"{index}. {query}")


print("\nSTEP 2: SEARCHING PUBMED")
print("=========================")

result = collect_candidate_papers(
    queries=queries,
    max_results_per_query=10
)

print("\nCANDIDATE PAPER RESULT")
print("======================")

print("Total unique candidates:")
print(result["total_candidates"])

print("\nPapers:")

for index, paper in enumerate(result["papers"], start=1):

    print(f"\n{index}. {paper['title']}")
    print(f"PubMed ID: {paper['pubmed_id']}")
    print(f"Year: {paper['publication_year']}")
    print(f"Journal: {paper['journal']}")
    print(f"Query: {paper['discovery_query']}")