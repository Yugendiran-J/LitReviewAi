from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import ResearchProject, User
from ..services.end_to_end_pipeline_service import run_end_to_end_pipeline
from ..services.literature_source_service import get_literature_sources
from ..services.ollama_service import (
    OllamaTimeoutError,
    OllamaConnectionError,
    check_ollama_health,
)

SUPPORTED_SOURCES = {
    "pubmed",
    "openalex",
    "crossref",
    "arxiv",
    "ieee_xplore",
    "google_scholar",
}

router = APIRouter(
    prefix="/literature",
    tags=["Literature Review"]
)


class LiteraturePipelineRequest(BaseModel):
    project_id: int

    keyword: str
    domain: str | None = None

    population: str | None = None
    intervention: str | None = None
    comparison: str | None = None
    outcome: str | None = None
    study_type: str | None = None

    year_from: int | None = None
    year_to: int | None = None

    restriction: str | None = None
    limitations: str | None = None
    sources: list[str] = ["pubmed"]


@router.get("/sources")
def list_literature_sources():
    return {"sources": get_literature_sources()}


@router.post("/run")
def run_literature_review(
    request: LiteraturePipelineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        # ======================================================
        # PRE-FLIGHT: Check Ollama is reachable
        # ======================================================

        if not check_ollama_health():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Ollama is not running or not reachable. "
                    "Start the Ollama application or run `ollama serve` "
                    "before starting the literature review."
                ),
            )

        if (
            request.year_from is not None
            and request.year_to is not None
            and request.year_from > request.year_to
        ):
            raise HTTPException(
                status_code=400,
                detail="year_from cannot be greater than year_to."
            )

        selected_sources = list(
            dict.fromkeys(
                source.strip().lower()
                for source in request.sources
                if source.strip()
            )
        )
        unsupported_sources = set(selected_sources) - SUPPORTED_SOURCES
        if unsupported_sources:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported literature source(s): "
                    + ", ".join(sorted(unsupported_sources))
                ),
            )
        if not selected_sources:
            raise HTTPException(
                status_code=400,
                detail="Select at least one literature source.",
            )
        if "ieee_xplore" in selected_sources:
            ieee_source = next(
                source
                for source in get_literature_sources()
                if source["id"] == "ieee_xplore"
            )
            if not ieee_source["available"]:
                raise HTTPException(
                    status_code=400,
                    detail=ieee_source["description"],
                )
        if "google_scholar" in selected_sources:
            scholar_source = next(
                source
                for source in get_literature_sources()
                if source["id"] == "google_scholar"
            )
            if not scholar_source["available"]:
                raise HTTPException(
                    status_code=400,
                    detail=scholar_source["description"],
                )

        project = (
            db.query(ResearchProject)
            .filter(
                ResearchProject.id == request.project_id,
                ResearchProject.user_id == current_user.id,
            )
            .first()
        )
        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        result = run_end_to_end_pipeline(
            db=db,
            project_id=request.project_id,
            keyword=request.keyword,
            domain=request.domain,
            population=request.population,
            intervention=request.intervention,
            comparison=request.comparison,
            outcome=request.outcome,
            study_type=request.study_type,
            year_from=request.year_from,
            year_to=request.year_to,
            restriction=request.restriction,
            limitations=request.limitations,
            sources=selected_sources,
        )

        return {
            "success": True,
            "message": "Literature review pipeline completed successfully.",
            "data": result
        }

    except HTTPException:
        raise

    except OllamaConnectionError as error:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except OllamaTimeoutError as error:
        db.rollback()
        raise HTTPException(
            status_code=504,
            detail=str(error),
        ) from error

    except Exception as error:
        db.rollback()
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
