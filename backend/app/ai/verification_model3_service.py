import json
import math

from ..services.ollama_service import generate_text


def verify_evidence(
    claim: str,
    evidence_chunks: list[dict]
):
    """
    AI Model 3 verifies whether a claim is supported
    by retrieved evidence from the research paper.

    FAISS/RAG retrieval happens before this function.
    Ollama performs only the evidence verification.
    """

    # --------------------------------------------------------
    # Validate claim
    # --------------------------------------------------------

    if not claim or not claim.strip():

        raise ValueError(
            "Claim cannot be empty"
        )

    # --------------------------------------------------------
    # Validate evidence
    # --------------------------------------------------------

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

Page:
{chunk.get("page_number", "Unknown")}

Chunk ID:
{chunk.get("chunk_id", "Unknown")}

Text:
{chunk.get("chunk_text", "")}

--------------------------------
"""

    # --------------------------------------------------------
    # Model 3 verification prompt
    # --------------------------------------------------------

    prompt = f"""
You are AI Model 3 in a systematic literature review system.

Your task is to verify whether a research claim is supported
by evidence retrieved from the full text of a research paper.

CLAIM
=====

{claim}


PAPER EVIDENCE
==============

{evidence_text}


VERIFICATION RULES
==================

1. Use ONLY the supplied evidence.
2. Do not use outside knowledge.
3. Do not invent missing information.
4. Determine whether the evidence directly supports the claim.
5. If the evidence partially supports the claim, mark it as
   "Partially Supported".
6. If the evidence clearly contradicts the claim, mark it as
   "Not Supported".
7. If there is insufficient evidence, mark it as
   "Insufficient Evidence".
8. Identify the page numbers containing supporting evidence.
9. Give a short explanation.
10. Give a confidence score from 0 to 100.


RETURN ONLY VALID JSON

Use exactly this structure:

{{
    "verification": "Supported",
    "confidence": 90,
    "explanation": "The evidence directly supports the claim.",
    "evidence": [
        {{
            "page_number": 3,
            "evidence_text": "Supporting evidence from the paper."
        }}
    ]
}}

The verification value MUST be exactly one of:

Supported
Partially Supported
Not Supported
Insufficient Evidence
"""

    # --------------------------------------------------------
    # Call Ollama
    # --------------------------------------------------------

    response_text = generate_text(prompt, format="json")

    if not response_text:

        raise ValueError(
            "Model 3 verification returned an empty response"
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = json.loads(
            response_text
        )

    except json.JSONDecodeError:

        print("\nRAW MODEL 3 RESPONSE:")
        print(response_text)

        raise ValueError(
            "AI Model 3 returned invalid JSON"
        )

    if not isinstance(data, dict):
        raise ValueError(
            "Model 3 verification must return a JSON object."
        )

    # --------------------------------------------------------
    # Validate verification result
    # --------------------------------------------------------

    valid_results = [
        "Supported",
        "Partially Supported",
        "Not Supported",
        "Insufficient Evidence"
    ]

    verification = data.get(
        "verification"
    )

    if verification not in valid_results:

        raise ValueError(
            f"Invalid verification result: "
            f"{verification}"
        )

    # --------------------------------------------------------
    # Validate confidence
    # --------------------------------------------------------

    try:
        confidence = float(data["confidence"])
    except (KeyError, ValueError, TypeError) as error:
        raise ValueError(
            "Model 3 verification must return numeric confidence."
        ) from error
    if not math.isfinite(confidence) or not 0 <= confidence <= 100:
        raise ValueError(
            "Model 3 verification confidence must be between 0 and 100."
        )

    data["confidence"] = confidence

    explanation = data.get("explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError(
            "Model 3 verification must return an explanation."
        )

    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError(
            "Model 3 verification must return an evidence list."
        )
    for item in evidence:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("evidence_text"), str)
            or not item["evidence_text"].strip()
            or item.get("page_number") is None
        ):
            raise ValueError(
                "Model 3 verification returned an invalid evidence citation."
            )
    if verification in {"Supported", "Partially Supported"} and not evidence:
        raise ValueError(
            "A supported claim must include at least one evidence citation."
        )

    return data