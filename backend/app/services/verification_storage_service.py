from sqlalchemy.orm import Session

from ..models import Paper, EvidenceVerification
from .ollama_service import AI_MODEL_ID


def save_verification_result(
    db: Session,
    project_id: int,
    paper_id: int,
    verification_result: dict
):
    # -----------------------------------------
    # Check paper
    # -----------------------------------------

    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.project_id == project_id
        )
        .first()
    )

    if not paper:
        raise ValueError(
            "Paper not found for this project"
        )

    # -----------------------------------------
    # Extract verification data
    # -----------------------------------------

    claim = verification_result.get(
        "claim",
        ""
    )

    verification = verification_result.get(
        "verification",
        "Uncertain"
    )

    confidence = verification_result.get(
        "confidence",
        0
    )

    explanation = verification_result.get(
        "explanation",
        ""
    )

    evidence_items = verification_result.get(
        "evidence",
        []
    )

    # -----------------------------------------
    # Prepare evidence safely
    # -----------------------------------------

    evidence_text_parts = []
    evidence_location_parts = []

    if isinstance(evidence_items, str):
        evidence_text_parts.append(evidence_items)
        evidence_location_parts.append("Page Unknown")
    elif isinstance(evidence_items, list):
        for item in evidence_items:
            if isinstance(item, str):
                if item.strip():
                    evidence_text_parts.append(item.strip())
                    evidence_location_parts.append("Page Unknown")
            elif isinstance(item, dict):
                page_number = item.get("page_number", "Unknown")
                evidence_text = item.get(
                    "evidence_text",
                    item.get("text", "")
                )
                if evidence_text:
                    evidence_text_parts.append(str(evidence_text).strip())
                    evidence_location_parts.append(f"Page {page_number}")

    evidence_text = "\n\n".join(
        evidence_text_parts
    )

    evidence_location = ", ".join(
        evidence_location_parts
    )

    # -----------------------------------------
    # Save record
    # -----------------------------------------

    record = EvidenceVerification(
        paper_id=paper_id,
        claim=str(claim),
        verification=str(verification),
        confidence=str(confidence),
        explanation=str(explanation),
        evidence_text=evidence_text,
        evidence_location=evidence_location,
        ai_model=AI_MODEL_ID
    )

    db.add(record)

    db.commit()

    db.refresh(record)

    return record