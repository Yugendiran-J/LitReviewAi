from app.ai.model3_extraction_rag_service import (
    extract_paper_data_with_rag
)


PAPER_ID = 15

TITLE = (
    "Artificial Intelligence for Systematic "
    "Literature Review"
)

EXTRACTION_QUERY = """
Extract the study methodology, population,
intervention, comparison, dataset, sample size,
results, metrics, limitations and conclusion.
"""


print("\nMODEL 3 — STRUCTURED EXTRACTION")
print("================================")


result = extract_paper_data_with_rag(
    paper_id=PAPER_ID,
    title=TITLE,
    extraction_query=EXTRACTION_QUERY,
    top_k=8
)


data = result["extraction"]


print("\nPOPULATION")
print("==========")
print(data["population"])


print("\nINTERVENTION")
print("============")
print(data["intervention"])


print("\nCOMPARISON")
print("==========")
print(data["comparison"])


print("\nMETHODOLOGY")
print("===========")
print(data["methodology"])


print("\nDATASET")
print("=======")
print(data["dataset"])


print("\nSAMPLE SIZE")
print("===========")
print(data["sample_size"])


print("\nRESULTS")
print("=======")
print(data["results"])


print("\nMETRICS")
print("=======")
print(data["metrics"])


print("\nLIMITATIONS")
print("===========")
print(data["limitations"])


print("\nCONCLUSION")
print("=========")
print(data["conclusion"])


print("\nCONFIDENCE")
print("==========")
print(data["confidence"])


print("\nEVIDENCE")
print("========")

for evidence in data["evidence"]:

    print(
        f"\nPage {evidence['page_number']}:"
    )

    print(
        evidence["evidence_text"]
    )