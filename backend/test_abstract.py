from app.services.pubmed_service import (
    search_pubmed,
    fetch_pubmed_abstracts
)


print("\nSEARCHING PUBMED")
print("================")

ids = search_pubmed(
    query="artificial intelligence systematic review",
    max_results=3
)

print("PubMed IDs:")
print(ids)


print("\nFETCHING ABSTRACTS")
print("==================")

abstracts = fetch_pubmed_abstracts(ids)

for pubmed_id, abstract in abstracts.items():

    print("\n--------------------------------")
    print("PubMed ID:", pubmed_id)

    if abstract:
        print("Abstract:")
        print(abstract[:1000])

    else:
        print("No abstract available.")