import json
import re
from ..services.ollama_service import generate_text


# ============================================================
# QUERY CLEANING
# ============================================================

def clean_search_query(query: str) -> str:
    """
    Clean and validate an AI-generated PubMed search query.

    Invalid queries such as:
        (
        ))
        ((
        []
        {}
    are rejected.
    """

    if not query:
        return ""

    query = str(query).strip()

    # Remove markdown code fences
    query = query.replace("```json", "")
    query = query.replace("```", "")

    query = query.strip()

    # Remove surrounding quotes
    query = query.strip("\"'")

    # Normalize whitespace
    query = re.sub(
        r"\s+",
        " ",
        query
    ).strip()

    # Obviously invalid queries
    invalid_queries = {
        "",
        "(",
        ")",
        "((",
        "))",
        "[]",
        "{}",
        "[",
        "]"
    }

    if query in invalid_queries:
        return ""

    # Reject queries containing only symbols
    if not re.search(
        r"[A-Za-z0-9]",
        query
    ):
        return ""

    # Query must contain meaningful text
    alphanumeric_count = len(
        re.findall(
            r"[A-Za-z0-9]",
            query
        )
    )

    if alphanumeric_count < 5:
        return ""

    return query


# ============================================================
# GENERATE SEARCH QUERIES
# ============================================================

def generate_search_queries(
    keyword: str,
    domain: str | None = None,
    max_queries: int = 5
):
    """
    AI Model 1.

    Generates multiple PubMed search queries from
    the research topic.

    The generated queries are cleaned and validated
    before being returned.
    """

    if not keyword or not keyword.strip():

        raise ValueError(
            "Research keyword cannot be empty."
        )

    keyword = keyword.strip()

    if max_queries < 1:
        max_queries = 1

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are an expert systematic literature review researcher.

Generate PubMed search queries for the following research topic.

Research topic:
{keyword}

Research domain:
{domain or "General"}

Requirements:

1. Generate exactly {max_queries} useful search queries.
2. Queries must contain meaningful research keywords.
3. Queries must be suitable for PubMed.
4. Do not return empty queries.
5. Do not return symbols only.
6. Do not return queries such as:
   (
   ))
   ((
   []
   {{}}
7. Do not use markdown.
8. Return ONLY valid JSON.

Required JSON format:

{{
    "research_topic": "{keyword}",
    "queries": [
        "query 1",
        "query 2",
        "query 3",
        "query 4",
        "query 5"
    ]
}}
"""

    # --------------------------------------------------------
    # CALL OLLAMA
    # --------------------------------------------------------

    content = generate_text(
        prompt,
        format="json",
        max_output_tokens=512,
    )

    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:

        data = json.loads(
            content
        )

    except json.JSONDecodeError:

        # Try extracting JSON object
        match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL
        )

        if not match:

            raise ValueError(
                "AI Model 1 returned invalid JSON."
            )

        try:

            data = json.loads(
                match.group(0)
            )

        except json.JSONDecodeError:

            raise ValueError(
                "AI Model 1 JSON could not be parsed."
            )

    # --------------------------------------------------------
    # GET QUERIES
    # --------------------------------------------------------

    raw_queries = data.get(
        "queries",
        []
    )

    if not isinstance(
        raw_queries,
        list
    ):

        raise ValueError(
            "AI Model 1 queries field is not a list."
        )

    # --------------------------------------------------------
    # CLEAN QUERIES
    # --------------------------------------------------------

    cleaned_queries = []

    for query in raw_queries:

        cleaned_query = clean_search_query(
            query
        )

        if not cleaned_query:
            continue

        # Remove duplicates
        if cleaned_query.lower() in [
            existing.lower()
            for existing in cleaned_queries
        ]:
            continue

        cleaned_queries.append(
            cleaned_query
        )

    # --------------------------------------------------------
    # LIMIT QUERIES
    # --------------------------------------------------------

    cleaned_queries = cleaned_queries[
        :max_queries
    ]

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if not cleaned_queries:

        raise ValueError(
            "AI Model 1 did not generate any valid "
            "PubMed search queries."
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    research_topic = data.get(
        "research_topic",
        keyword
    )

    return {
        "research_topic": research_topic,
        "queries": cleaned_queries
    }