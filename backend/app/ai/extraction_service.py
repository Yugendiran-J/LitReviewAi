import json

from ..services.ollama_service import generate_text


def extract_research_data(
    title: str,
    query: str,
    retrieved_chunks: list[dict]
):
    if not retrieved_chunks:
        raise ValueError("No relevant evidence found")

    evidence_text = ""

    for index, chunk in enumerate(retrieved_chunks, start=1):
        evidence_text += f"""
Evidence {index}
Page: {chunk["page_number"]}
Chunk ID: {chunk["chunk_id"]}

{chunk["chunk_text"]}

--------------------------------
"""

    prompt = f"""
You are an AI assistant for systematic literature review data extraction.

Your task is to extract research information ONLY from the provided evidence.

Do not invent information.

If a field is not available in the evidence, return "Not reported".

Research Paper:
Title: {title}

Extraction Request:
{query}

Evidence from the paper:
{evidence_text}

Return ONLY valid JSON in the following format:

{{
    "population": "string",
    "intervention": "string",
    "comparison": "string",
    "methodology": "string",
    "dataset": "string",
    "sample_size": "string",
    "results": "string",
    "metrics": "string",
    "limitations": "string",
    "conclusion": "string",
    "evidence": [
        {{
            "page_number": 1,
            "evidence_text": "exact supporting text"
        }}
    ],
    "confidence": 0
}}

Confidence must be a number between 0 and 100.

Important rules:
1. Use only the supplied evidence.
2. Do not hallucinate missing information.
3. Keep evidence directly connected to the extracted information.
4. Mention page numbers whenever evidence is available.
5. Return valid JSON only.
"""

    result = generate_text(prompt, format="json")

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        raise ValueError("AI returned invalid JSON")