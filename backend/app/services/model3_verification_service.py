from sqlalchemy.orm import Session

from ..models import Paper
from ..ai.model3_rag_service import verify_claim_with_rag
from .verification_storage_service import save_verification_result


def process_model3_verification(
    db: Session,
    project_id: int,
    paper_id: int,
    claim: str
):
    # -----------------------------------------
    # 1. Find paper
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
    # 2. Check full text
    # -----------------------------------------

    if not paper.full_text:
        raise ValueError(
            "Full text is not available for this paper"
        )

    # -----------------------------------------
    # 3. Model 3 + RAG
    # -----------------------------------------

    result = verify_claim_with_rag(
        paper_id=paper_id,
        claim=claim,
        top_k=5
    )

    verification = result.get("verification", {})

    # -----------------------------------------
    # 4. Normalize verification data safely
    # -----------------------------------------

    if isinstance(verification, dict):
        ver_status = verification.get("verification", "Uncertain")
        confidence = verification.get("confidence", 0)
        explanation = verification.get("explanation", "")
        evidence = verification.get("evidence", [])
    elif isinstance(verification, str):
        ver_status = verification
        confidence = 0
        explanation = ""
        evidence = []
    else:
        ver_status = "Uncertain"
        confidence = 0
        explanation = ""
        evidence = []

    verification_to_save = {
        "claim": claim,
        "verification": ver_status,
        "confidence": confidence,
        "explanation": explanation,
        "evidence": evidence,
    }

    # -----------------------------------------
    # 5. Save to MySQL
    # -----------------------------------------

    saved_record = save_verification_result(
        db=db,
        project_id=project_id,
        paper_id=paper_id,
        verification_result=verification_to_save
    )

    return {
        "project_id": project_id,
        "paper_id": paper_id,
        "title": paper.title,
        "claim": claim,
        "verification": verification_to_save,
        "verification_id": saved_record.id
    }