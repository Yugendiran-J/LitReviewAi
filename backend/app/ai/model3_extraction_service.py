import json
import math

from ..services.ollama_service import generate_text


def extract_research_data_from_evidence(
    title: str,
    evidence_chunks: list[dict]
):
    """
    Extract structured research information only from
    evidence retrieved from the full-text paper.

    The evidence is retrieved by the existing FAISS/RAG
    pipeline. Ollama is used only for the extraction step.
    """

    if not evidence_chunks:
        raise ValueError(
            "No evidence chunks provided"
        )

    # --------------------------------------------------------
    # Build evidence text
    # --------------------------------------------------------

    evidence_text = ""

    for index, chunk in enumerate(
        evidence_chunks,
        start=1
    ):

        evidence_text += f"""
Evidence {index}

Page Number:
{chunk.get("page_number", "Unknown")}

Chunk ID:
{chunk.get("chunk_id", "Unknown")}

Text:
{chunk.get("chunk_text", "")}

--------------------------------
"""

    # --------------------------------------------------------
    # Model 3 extraction prompt
    # --------------------------------------------------------

    prompt = f"""
You are AI Model 3 in a systematic literature review system.

Your task is to extract structured research information from
the provided evidence of a research paper.

IMPORTANT:

Use ONLY the supplied evidence.

Do not use outside knowledge.

Do not invent information.

If a field is not available in the evidence, return:
"Not reported"


RESEARCH PAPER
==============

Title:
{title}


EVIDENCE FROM FULL TEXT
=======================

{evidence_text}


EXTRACTION FIELDS
=================

Extract the following:

1. Population
2. Intervention
3. Comparison
4. Methodology
5. Dataset
6. Sample Size
7. Results
8. Metrics
9. Limitations
10. Conclusion


EVIDENCE REQUIREMENT
====================

For important extracted information, provide the supporting
evidence text and page number.

Only provide evidence that actually appears in the supplied
paper evidence.


CONFIDENCE
==========

Give an overall extraction confidence from 0 to 100.


RETURN ONLY VALID JSON

Use exactly this structure:

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
            "evidence_text": "Supporting text from the paper"
        }}
    ],
    "confidence": 0
}}
"""

    # --------------------------------------------------------
    # Call Ollama
    # --------------------------------------------------------

    response_text = generate_text(prompt, format="json")

    if not response_text:
        raise ValueError(
            "Model 3 extraction returned an empty response"
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = json.loads(response_text)

    except json.JSONDecodeError:

        print("\nRAW MODEL 3 RESPONSE:")
        print(response_text)

        raise ValueError(
            "Model 3 returned invalid JSON"
        )

    if not isinstance(data, dict):
        raise ValueError(
            "Model 3 extraction must return a JSON object."
        )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [
        "population",
        "intervention",
        "comparison",
        "methodology",
        "dataset",
        "sample_size",
        "results",
        "metrics",
        "limitations",
        "conclusion"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]
    if missing_fields:
        raise ValueError(
            "Model 3 extraction omitted required fields: "
            + ", ".join(missing_fields)
        )

    for field in required_fields:
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(
                f"Model 3 extraction returned an invalid {field} value."
            )

    # --------------------------------------------------------
    # Validate evidence
    # --------------------------------------------------------

    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError(
            "Model 3 extraction must return an evidence list."
        )
    for item in evidence:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("evidence_text"), str)
            or not item["evidence_text"].strip()
            or item.get("page_number") is None
        ):
            raise ValueError(
                "Model 3 extraction returned an invalid evidence citation."
            )

    # --------------------------------------------------------
    # Validate confidence
    # --------------------------------------------------------

    try:
        confidence = float(data["confidence"])
    except (KeyError, ValueError, TypeError) as error:
        raise ValueError(
            "Model 3 extraction must return numeric confidence."
        ) from error
    if not math.isfinite(confidence) or not 0 <= confidence <= 100:
        raise ValueError(
            "Model 3 extraction confidence must be between 0 and 100."
        )

    data["confidence"] = confidence

    return data