from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ResearchProject,
    PICOSCriteria,
    Paper,
    ScreeningResult,
    User
)
from ..dependencies import get_current_user
from ..schemas import (
    ScreeningResponse,
    ScreeningResultResponse,
    HumanReviewResponse,
    ScreeningSummaryResponse
)
from ..ai.screening_service import screen_paper
from ..services.ollama_service import AI_MODEL_ID


def get_confidence_level(confidence_score):
    try:
        score = float(confidence_score)
    except (ValueError, TypeError):
        return "Low"

    if score >= 80:
        return "High"

    if score >= 60:
        return "Medium"

    return "Low"


router = APIRouter(
    prefix="/projects/{project_id}/screening",
    tags=["AI Screening"]
)


@router.post(
    "/papers/{paper_id}",
    response_model=ScreeningResponse
)
def screen_single_paper(
    project_id: int,
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check project ownership
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Get PICOS criteria
    picos = (
        db.query(PICOSCriteria)
        .filter(
            PICOSCriteria.project_id == project_id
        )
        .first()
    )

    if picos is None:
        raise HTTPException(
            status_code=400,
            detail="PICOS criteria not found"
        )

    # Get paper
    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.project_id == project_id
        )
        .first()
    )

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    # Abstract is required for screening
    if not paper.abstract:
        raise HTTPException(
            status_code=400,
            detail="Paper abstract is not available"
        )

    try:

        # Send paper + PICOS to AI
        ai_result = screen_paper(
            title=paper.title,
            abstract=paper.abstract,
            population=picos.population or "",
            intervention=picos.intervention or "",
            comparison=picos.comparison or "",
            outcome=picos.outcome or "",
            study_type=picos.study_type or ""
        )

        # Default values
        decision = "Uncertain"
        confidence = None
        reason = ai_result

        # Extract decision
        for possible_decision in [
            "Include",
            "Exclude",
            "Uncertain"
        ]:
            if f"Decision: {possible_decision}" in ai_result:
                decision = possible_decision
                break

        # Extract confidence
        if "Confidence:" in ai_result:
            confidence_text = ai_result.split(
                "Confidence:", 1
            )[1].split(
                "\n", 1
            )[0].strip()

            confidence = confidence_text

        # Extract reason
        if "Reason:" in ai_result:
            reason = ai_result.split(
                "Reason:", 1
            )[1].strip()

        # Save screening result
        screening_result = ScreeningResult(
            paper_id=paper.id,
            decision=decision,
            confidence_score=confidence,
            reason=reason,
            ai_model=AI_MODEL_ID
        )

        db.add(screening_result)
        db.commit()
        db.refresh(screening_result)

        return screening_result

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"AI screening failed: {str(e)}"
        )


@router.post(
    "/all",
    response_model=list[ScreeningResponse]
)
def screen_all_papers(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check project ownership
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Get PICOS criteria
    picos = (
        db.query(PICOSCriteria)
        .filter(
            PICOSCriteria.project_id == project_id
        )
        .first()
    )

    if picos is None:
        raise HTTPException(
            status_code=400,
            detail="PICOS criteria not found"
        )

    # Get all papers
    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    if not papers:
        raise HTTPException(
            status_code=400,
            detail="No papers found in this project"
        )

    results = []

    for paper in papers:

        # Skip papers without abstracts
        if not paper.abstract:
            continue

        try:

            # Send paper + PICOS to AI
            ai_result = screen_paper(
                title=paper.title,
                abstract=paper.abstract,
                population=picos.population or "",
                intervention=picos.intervention or "",
                comparison=picos.comparison or "",
                outcome=picos.outcome or "",
                study_type=picos.study_type or ""
            )

            decision = "Uncertain"
            confidence = None
            reason = ai_result

            # Extract decision
            for possible_decision in [
                "Include",
                "Exclude",
                "Uncertain"
            ]:
                if f"Decision: {possible_decision}" in ai_result:
                    decision = possible_decision
                    break

            # Extract confidence
            if "Confidence:" in ai_result:

                confidence = (
                    ai_result
                    .split("Confidence:", 1)[1]
                    .split("\n", 1)[0]
                    .strip()
                )

            # Extract reason
            if "Reason:" in ai_result:

                reason = (
                    ai_result
                    .split("Reason:", 1)[1]
                    .strip()
                )

            # Save result
            screening_result = ScreeningResult(
                paper_id=paper.id,
                decision=decision,
                confidence_score=confidence,
                reason=reason,
                ai_model=AI_MODEL_ID
            )

            db.add(screening_result)
            db.flush()

            results.append(screening_result)

        except Exception as e:

            print(
                f"Screening failed for paper "
                f"{paper.id}: {str(e)}"
            )

            continue

    db.commit()

    return results

@router.get(
    "/results",
    response_model=list[ScreeningResultResponse]
)
def get_screening_results(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check project ownership
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Get project papers
    papers = (
        db.query(Paper.id)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    paper_ids = [paper_id for (paper_id,) in papers]

    if not paper_ids:
        return []

    # Get screening results
    results = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.paper_id.in_(paper_ids)
        )
        .order_by(ScreeningResult.id.desc())
        .all()
    )

    response = []

    for result in results:

        confidence_level = get_confidence_level(
            result.confidence_score
        )

        response.append({
            "id": result.id,
            "paper_id": result.paper_id,
            "decision": result.decision,
            "confidence_score": result.confidence_score,
            "confidence_level": confidence_level,
            "reason": result.reason,
            "ai_model": result.ai_model
        })

    return response
def get_screening_results(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check project ownership
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Get all papers belonging to this project
    papers = (
        db.query(Paper.id)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    paper_ids = [paper_id for (paper_id,) in papers]

    if not paper_ids:
        return []

    # Get screening results
    results = (
        db.query(ScreeningResult)
        .filter(
            ScreeningResult.paper_id.in_(paper_ids)
        )
        .order_by(ScreeningResult.id.desc())
        .all()
    )

    return results

@router.get(
    "/human-review",
    response_model=list[HumanReviewResponse]
)
def get_human_review_queue(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check project ownership
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Get papers and their latest screening result
    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    review_queue = []

    for paper in papers:

        screening_result = (
            db.query(ScreeningResult)
            .filter(
                ScreeningResult.paper_id == paper.id
            )
            .order_by(ScreeningResult.id.desc())
            .first()
        )

        if screening_result is None:
            continue

        # Convert confidence to number
        try:
            confidence = float(
                screening_result.confidence_score
            )
        except (ValueError, TypeError):
            confidence = 0

        # Send uncertain or low-confidence papers for review
        if (
            screening_result.decision == "Uncertain"
            or confidence < 80
        ):

            confidence_level = get_confidence_level(
                screening_result.confidence_score
            )

            review_queue.append({
                "screening_id": screening_result.id,
                "paper_id": paper.id,
                "paper_title": paper.title,
                "decision": screening_result.decision,
                "confidence_score": screening_result.confidence_score,
                "confidence_level": confidence_level,
                "reason": screening_result.reason
            })

    return review_queue

@router.get(
    "/summary",response_model=ScreeningSummaryResponse
)
def get_screening_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check project ownership
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Get all papers
    papers = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )

    total_papers = len(papers)

    included = 0
    excluded = 0
    uncertain = 0
    human_review = 0

    for paper in papers:

        # Get latest screening result
        screening_result = (
            db.query(ScreeningResult)
            .filter(
                ScreeningResult.paper_id == paper.id
            )
            .order_by(ScreeningResult.id.desc())
            .first()
        )

        if screening_result is None:
            continue

        decision = screening_result.decision

        if decision == "Include":
            included += 1

        elif decision == "Exclude":
            excluded += 1

        elif decision == "Uncertain":
            uncertain += 1

        # Check confidence
        try:
            confidence = float(
                screening_result.confidence_score
            )
        except (ValueError, TypeError):
            confidence = 0

        if decision == "Uncertain" or confidence < 80:
            human_review += 1

    return {
        "total_papers": total_papers,
        "included": included,
        "excluded": excluded,
        "uncertain": uncertain,
        "human_review": human_review
    }
