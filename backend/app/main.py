from fastapi import FastAPI
from sqlalchemy import text
from .routes.literature_pipeline_router import router as literature_pipeline_router

from .database import engine
from . import models

from .routers.auth_router import router as auth_router
from .routers.project_router import router as project_router
from .routers.picos_router import router as picos_router
from .routers.paper_router import router as paper_router
from .routers.search_router import router as search_router
from .routers.screening_router import router as screening_router
from .routers.feedback_router import router as feedback_router
from .routers.upload_router import router as upload_router
from .routers.chunk_router import router as chunk_router
from .routers.vector_router import router as vector_router
from .routers.extraction_router import router as extraction_router
from .routers.verification_router import router as verification_router
from .routers.extraction_validation_router import router as extraction_validation_router
from .routers.summary_router import router as summary_router
from .routers.project_summary_router import router as project_summary_router
from .routers.project_papers_router import router as project_papers_router
from .routers.review_queue_router import router as review_queue_router
from .routers.screening_statistics_router import router as screening_statistics_router
from .routers.extraction_statistics_router import router as extraction_statistics_router
from .routers.feedback_statistics_router import router as feedback_statistics_router
from .routers.dashboard_router import router as dashboard_router
from .routers.paper_upload_router import router as paper_upload_router
from .routers.human_feedback_router import router as human_feedback_router
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="LitReviewAI API",
    description="AI-assisted discovery and evidence assessment for candidate base papers",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(project_router)
app.include_router(picos_router)
app.include_router(project_papers_router)
app.include_router(paper_router)
app.include_router(search_router)
app.include_router(screening_router)
app.include_router(feedback_router)
app.include_router(upload_router)
app.include_router(chunk_router)
app.include_router(vector_router)
app.include_router(extraction_router)
app.include_router(verification_router)
app.include_router(extraction_validation_router)
app.include_router(summary_router)
app.include_router(project_summary_router)
app.include_router(review_queue_router)
app.include_router(screening_statistics_router)
app.include_router(extraction_statistics_router)
app.include_router(feedback_statistics_router)
app.include_router(dashboard_router)
app.include_router(paper_upload_router)
app.include_router(
    human_feedback_router
)
app.include_router(
    literature_pipeline_router
)


@app.get("/")
def root():
    return {
        "message": "LitReviewAI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/database-test")
def database_test():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected"
    }
