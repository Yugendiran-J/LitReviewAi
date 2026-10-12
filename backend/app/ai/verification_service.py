import json

from ..services.ollama_service import generate_text


def verify_extraction(
    extracted_field: str,
    extracted_value: str,
    evidence_text: str
):
    prompt = f"""
You are an evidence verification assistant for a systematic literature review.

Verify whether the extracted information is supported by the provided evidence.

Extracted Field:
{extracted_field}

Extracted Value:
{extracted_value}

Paper Evidence:
{evidence_text}

Return ONLY valid JSON:

{{
    "verified": true,
    "confidence": 0,
    "explanation": "short explanation"
}}

Rules:
1. verified must be true or false.
2. confidence must be between 0 and 100.
3. Use ONLY the provided evidence.
4. Do not add information that is not present in the evidence.
5. If the evidence does not support the extracted value, verified must be false.
"""

    result = generate_text(prompt, format="json")

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        raise ValueError("AI returned invalid verification JSON")