from ..services.ollama_service import generate_text


def screen_paper(
    title: str,
    abstract: str,
    population: str,
    intervention: str,
    comparison: str,
    outcome: str,
    study_type: str
):

    prompt = f"""
You are an AI assistant for systematic literature review screening.

Evaluate whether the following research paper matches the given PICOS criteria.

PICOS Criteria:

Population:
{population}

Intervention:
{intervention}

Comparison:
{comparison}

Outcome:
{outcome}

Study Type:
{study_type}

Research Paper:

Title:
{title}

Abstract:
{abstract}

Return your decision using exactly one of:

Include
Exclude
Uncertain

Also provide:

Confidence:
A number between 0 and 100.

Reason:
A short explanation of why the paper matches or does not match the PICOS criteria.

Return the result in this format:

Decision: Include/Exclude/Uncertain
Confidence: 0-100
Reason: explanation
"""

    return generate_text(prompt)