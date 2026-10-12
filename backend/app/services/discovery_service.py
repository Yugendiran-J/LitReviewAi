import json
import re

from .ollama_service import AI_MODEL_ID, generate_text


def clean_json_response(text: str) -> str:
    """
    Remove markdown code fences if the model returns JSON inside ```json ... ```
    """

    if not text:
        return ""

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def validate_queries(queries):
    """
    Validate and clean AI-generated PubMed queries.
    """

    if not isinstance(queries, list):
        raise ValueError("AI response must contain a list of queries.")

    cleaned_queries = []

    for query in queries:

        if not isinstance(query, str):
            continue

        query = query.strip()

        if not query:
            continue

        # Remove unnecessary numbering such as:
        # 1. query
        # 2) query
        query = re.sub(
            r"^\s*\d+[\.\)]\s*",
            "",
            query
        )

        query = query.strip()

        if len(query) < 3:
            continue

        cleaned_queries.append(query)

    # Remove duplicates while preserving order
    cleaned_queries = list(
        dict.fromkeys(cleaned_queries)
    )

    if not cleaned_queries:
        raise ValueError(
            "AI Model 1 did not generate valid search queries."
        )

    return cleaned_queries


def generate_search_queries(
    research_topic: str,
    research_question: str | None = None,
    population: str | None = None,
    intervention: str | None = None,
    comparison: str | None = None,
    outcome: str | None = None,
    study_type: str | None = None,
    sources: list[str] | None = None,
):
    """
    AI Model 1:
    Generate search queries suitable for the selected literature sources.
    """

    if not research_topic or not research_topic.strip():
        raise ValueError(
            "Research topic cannot be empty."
        )

    prompt = f"""
You are an expert systematic literature review researcher.

Your task is to generate exactly 5 high-quality search queries for a
systematic literature review. Make the query text suitable for the selected
sources; do not use PubMed-specific field tags unless PubMed is the only source.

Selected literature sources:
{", ".join(sources or ["pubmed"])}

Research topic:
{research_topic}

Research question:
{research_question or "Not specified"}

PICOS information:

Population:
{population or "Not specified"}

Intervention:
{intervention or "Not specified"}

Comparison:
{comparison or "Not specified"}

Outcome:
{outcome or "Not specified"}

Study type:
{study_type or "Not specified"}

Requirements:

1. Generate exactly 5 different search queries.
2. Queries must be portable across the selected sources and not depend on
   platform-specific syntax.
3. Use important keywords and synonyms.
4. Use Boolean operators such as AND, OR when appropriate.
5. Keep the queries focused on the research topic.
6. Avoid overly broad queries.
7. Do not include explanations.
8. Return ONLY valid JSON.

Required JSON format:

{{
    "queries": [
        "query 1",
        "query 2",
        "query 3",
        "query 4",
        "query 5"
    ]
}}
"""

    response_text = generate_text(
        prompt,
        format="json",
        max_output_tokens=512,
    )

    if not response_text:
        raise ValueError(
            "AI Model 1 returned an empty response."
        )

    cleaned_response = clean_json_response(
        response_text
    )

    try:
        result = json.loads(cleaned_response)

    except json.JSONDecodeError as error:
        print("\nInvalid JSON returned by Ollama:")
        print(response_text)

        raise ValueError(
            f"AI Model 1 returned invalid JSON: {error}"
        )

    if not isinstance(result, dict):
        raise ValueError(
            "AI Model 1 must return a JSON object containing search queries."
        )

    queries = result.get("queries")

    queries = validate_queries(queries)

    # Keep maximum 5 queries
    queries = queries[:5]

    return {
        "queries": queries,
        "total_queries": len(queries),
        "ai_model": AI_MODEL_ID
    }