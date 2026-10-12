from pydantic import BaseModel, EmailStr
from pydantic import BaseModel


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(TokenResponse):
    user: UserResponse


class ProjectCreate(BaseModel):
    title: str
    research_question: str
    description: str | None = None
    domain: str | None = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    research_question: str
    description: str | None
    domain: str | None
    status: str

class ProjectUpdate(BaseModel):
    title: str | None = None
    research_question: str | None = None
    description: str | None = None
    domain: str | None = None
    status: str | None = None

class PICOSCreate(BaseModel):
    population: str | None = None
    intervention: str | None = None
    comparison: str | None = None
    outcome: str | None = None
    study_type: str | None = None
    additional_criteria: str | None = None

class PICOSResponse(BaseModel):
    id: int
    project_id: int
    population: str | None
    intervention: str | None
    comparison: str | None
    outcome: str | None
    study_type: str | None
    additional_criteria: str | None

class PICOSUpdate(BaseModel):
    population: str | None = None
    intervention: str | None = None
    comparison: str | None = None
    outcome: str | None = None
    study_type: str | None = None
    additional_criteria: str | None = None

class PaperCreate(BaseModel):
    title: str
    authors: str | None = None
    abstract: str | None = None
    publication_year: int | None = None
    journal: str | None = None
    doi: str | None = None
    url: str | None = None
    source: str | None = None
    pdf_path: str | None = None

class PaperResponse(BaseModel):
    id: int
    project_id: int
    title: str
    authors: str | None
    abstract: str | None
    full_text: str | None
    publication_year: int | None
    journal: str | None
    doi: str | None
    url: str | None
    source: str | None
    pdf_path: str | None

class PaperUpdate(BaseModel):
    title: str | None = None
    authors: str | None = None
    abstract: str | None = None
    publication_year: int | None = None
    journal: str | None = None
    doi: str | None = None
    url: str | None = None
    source: str | None = None
    pdf_path: str | None = None

class LiteratureSearchRequest(BaseModel):
    query: str
    max_results: int = 10

class LiteratureSearchResponse(BaseModel):
    pubmed_id: str
    title: str | None
    authors: str | None
    publication_year: int | None
    journal: str | None
    source: str
    url: str
    saved: bool = False
    paper_id: int | None = None

class ScreeningResponse(BaseModel):
    paper_id: int
    decision: str
    confidence_score: str | None
    reason: str | None
    ai_model: str | None

class ScreeningResultResponse(BaseModel):
    id: int
    paper_id: int
    decision: str
    confidence_score: str | None
    confidence_level: str
    reason: str | None
    ai_model: str | None


class HumanFeedbackCreate(BaseModel):
    corrected_decision: str
    feedback_text: str | None = None
    reviewer_name: str | None = None


class HumanFeedbackResponse(BaseModel):
    id: int
    paper_id: int
    original_decision: str | None
    corrected_decision: str | None
    feedback_text: str | None
    reviewer_name: str | None

class HumanReviewResponse(BaseModel):
    screening_id: int
    paper_id: int
    paper_title: str
    decision: str
    confidence_score: str | None
    confidence_level: str
    reason: str | None

class ScreeningSummaryResponse(BaseModel):
    total_papers: int
    included: int
    excluded: int
    uncertain: int
    human_review: int

class PaperChunkResponse(BaseModel):
    id: int
    paper_id: int
    chunk_index: int
    page_number: int
    chunk_text: str

class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 3


class SemanticSearchResult(BaseModel):
    chunk_id: int
    chunk_index: int
    page_number: int
    chunk_text: str
    distance: float

class ExtractionRequest(BaseModel):
    query: str
    top_k: int = 5


class ExtractionResponse(BaseModel):
    id: int
    paper_id: int
    population: str | None = None
    intervention: str | None = None
    comparison: str | None = None
    methodology: str | None = None
    dataset: str | None = None
    sample_size: str | None = None
    results: str | None = None
    metrics: str | None = None
    limitations: str | None = None
    conclusion: str | None = None
    evidence_text: str | None = None
    evidence_location: str | None = None
    extraction_confidence: str | None = None

class VerificationRequest(BaseModel):
    field_name: str
    extracted_value: str


class VerificationResponse(BaseModel):
    field_name: str
    extracted_value: str
    verified: bool
    confidence: float
    explanation: str

class ExtractionValidationRequest(BaseModel):
    field_name: str
    original_value: str
    corrected_value: str | None = None
    status: str
    feedback: str | None = None
    reviewer_name: str | None = None


class ExtractionValidationResponse(BaseModel):
    message: str
    extraction_id: int
    field_name: str
    status: str
    final_value: str | None = None

class PaperSummaryResponse(BaseModel):
    paper_id: int
    title: str
    authors: str | None = None
    abstract: str | None = None
    publication_year: int | None = None
    journal: str | None = None
    doi: str | None = None
    source: str | None = None

    screening_decision: str | None = None
    screening_confidence: str | None = None
    screening_reason: str | None = None

    extraction_id: int | None = None
    population: str | None = None
    intervention: str | None = None
    comparison: str | None = None
    methodology: str | None = None
    dataset: str | None = None
    sample_size: str | None = None
    results: str | None = None
    metrics: str | None = None
    limitations: str | None = None
    conclusion: str | None = None

    evidence_text: str | None = None
    evidence_location: str | None = None
    extraction_confidence: str | None = None

    feedback_count: int = 0

class ProjectSummaryResponse(BaseModel):
    project_id: int
    project_title: str
    research_question: str
    status: str

    total_papers: int
    included_papers: int
    excluded_papers: int
    uncertain_papers: int

    papers_with_pdf: int
    papers_with_extraction: int
    total_feedback: int

class ProjectPaperResponse(BaseModel):
    paper_id: int
    title: str
    authors: str | None = None
    publication_year: int | None = None
    journal: str | None = None
    source: str | None = None

    screening_decision: str | None = None
    screening_confidence: str | None = None
    screening_reason: str | None = None

    has_pdf: bool
    has_extraction: bool

class ScreeningReviewResponse(BaseModel):
    paper_id: int
    title: str
    abstract: str | None = None

    ai_decision: str
    confidence_score: str | None = None
    confidence_level: str
    reason: str | None = None

    publication_year: int | None = None
    journal: str | None = None

class ScreeningStatisticsResponse(BaseModel):
    project_id: int
    total_papers: int
    included: int
    excluded: int
    uncertain: int
    not_screened: int

class ExtractionStatisticsResponse(BaseModel):
    project_id: int
    total_papers: int
    extracted_papers: int
    not_extracted_papers: int

class FeedbackStatisticsResponse(BaseModel):
    project_id: int
    total_feedback: int
    accepted_feedback: int
    corrected_feedback: int

class DashboardResponse(BaseModel):
    project_id: int
    project_title: str
    research_question: str
    status: str

    total_papers: int

    included_papers: int
    excluded_papers: int
    uncertain_papers: int
    not_screened: int

    papers_with_pdf: int

    extracted_papers: int
    not_extracted_papers: int

    total_feedback: int
    accepted_feedback: int
    corrected_feedback: int