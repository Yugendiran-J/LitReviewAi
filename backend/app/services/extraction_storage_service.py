from sqlalchemy.orm import Session

from ..models import Paper, ExtractedData


def save_extraction_result(
    db: Session,
    project_id: int,
    paper_id: int,
    extraction: dict
):
    """
    Save or update Model 3 structured extraction
    in the extracted_data table.
    """

    # --------------------------------------------------------
    # 1. Verify paper belongs to project
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 2. Prepare evidence safely
    # --------------------------------------------------------

    evidence_items = extraction.get(
        "evidence",
        []
    )

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
                text = item.get(
                    "evidence_text",
                    item.get("text", "")
                )
                if text:
                    evidence_text_parts.append(str(text).strip())
                    evidence_location_parts.append(f"Page {page_number}")

    evidence_text = "\n\n".join(
        evidence_text_parts
    )

    evidence_location = ", ".join(
        evidence_location_parts
    )

    # --------------------------------------------------------
    # 3. Check existing extraction
    # --------------------------------------------------------

    existing = (
        db.query(ExtractedData)
        .filter(
            ExtractedData.paper_id == paper_id
        )
        .first()
    )

    # --------------------------------------------------------
    # 4. Update existing extraction
    # --------------------------------------------------------

    if existing:

        existing.population = str(extraction.get("population", "Not reported"))
        existing.intervention = str(extraction.get("intervention", "Not reported"))
        existing.comparison = str(extraction.get("comparison", "Not reported"))
        existing.methodology = str(extraction.get("methodology", "Not reported"))
        existing.dataset = str(extraction.get("dataset", "Not reported"))
        existing.sample_size = str(extraction.get("sample_size", "Not reported"))
        existing.results = str(extraction.get("results", "Not reported"))
        existing.metrics = str(extraction.get("metrics", "Not reported"))
        existing.limitations = str(extraction.get("limitations", "Not reported"))
        existing.conclusion = str(extraction.get("conclusion", "Not reported"))
        existing.evidence_text = evidence_text
        existing.evidence_location = evidence_location
        existing.extraction_confidence = str(
            extraction.get(
                "confidence",
                0
            )
        )

        saved_record = existing

    # --------------------------------------------------------
    # 5. Create new extraction
    # --------------------------------------------------------

    else:

        saved_record = ExtractedData(
            paper_id=paper_id,

            population=str(extraction.get("population", "Not reported")),
            intervention=str(extraction.get("intervention", "Not reported")),
            comparison=str(extraction.get("comparison", "Not reported")),
            methodology=str(extraction.get("methodology", "Not reported")),
            dataset=str(extraction.get("dataset", "Not reported")),
            sample_size=str(extraction.get("sample_size", "Not reported")),
            results=str(extraction.get("results", "Not reported")),
            metrics=str(extraction.get("metrics", "Not reported")),
            limitations=str(extraction.get("limitations", "Not reported")),
            conclusion=str(extraction.get("conclusion", "Not reported")),

            evidence_text=evidence_text,
            evidence_location=evidence_location,

            extraction_confidence=str(
                extraction.get(
                    "confidence",
                    0
                )
            )
        )

        db.add(saved_record)

    # --------------------------------------------------------
    # 6. Save
    # --------------------------------------------------------

    db.commit()

    db.refresh(saved_record)

    return saved_record