from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    projects = relationship(
        "ResearchProject",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(String(255), nullable=False)

    research_question = Column(Text, nullable=False)

    description = Column(Text, nullable=True)

    domain = Column(String(150), nullable=True)

    status = Column(
        String(50),
        default="draft",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="projects"
    )

    picos = relationship(
        "PICOSCriteria",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    papers = relationship(
        "Paper",
        back_populates="project",
        cascade="all, delete-orphan"
    )


class PICOSCriteria(Base):
    __tablename__ = "picos_criteria"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id"),
        nullable=False
    )

    population = Column(Text, nullable=True)

    intervention = Column(Text, nullable=True)

    comparison = Column(Text, nullable=True)

    outcome = Column(Text, nullable=True)

    study_type = Column(Text, nullable=True)

    additional_criteria = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    project = relationship(
        "ResearchProject",
        back_populates="picos"
    )

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    pubmed_id = Column(String(50), nullable=True, index=True)

    project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False)
    title = Column(Text, nullable=False)

    authors = Column(Text, nullable=True)

    abstract = Column(Text, nullable=True)

    publication_year = Column(Integer, nullable=True)

    journal = Column(String(255), nullable=True)

    doi = Column(String(255), nullable=True)

    url = Column(Text, nullable=True)

    source = Column(String(100), nullable=True)

    pdf_path = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    project = relationship(
        "ResearchProject",
        back_populates="papers"
    )
    chunks = relationship(
    "PaperChunk",
    back_populates="paper",
    cascade="all, delete-orphan"
)   
    evidence_verifications = relationship(
    "EvidenceVerification",
    back_populates="paper",
    cascade="all, delete-orphan"
)

    screening_results = relationship(
        "ScreeningResult",
        back_populates="paper",
        cascade="all, delete-orphan"
    )

    extracted_data = relationship(
        "ExtractedData",
        back_populates="paper",
        cascade="all, delete-orphan"
    )


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, index=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id"),
        nullable=False
    )

    decision = Column(
        String(30),
        nullable=False
    )

    confidence_score = Column(
        String(20),
        nullable=True
    )

    reason = Column(
        Text,
        nullable=True
    )

    ai_model = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    paper = relationship(
        "Paper",
        back_populates="screening_results"
    )

class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, index=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id"),
        nullable=False
    )

    population = Column(Text, nullable=True)

    intervention = Column(Text, nullable=True)

    comparison = Column(Text, nullable=True)

    methodology = Column(Text, nullable=True)

    dataset = Column(Text, nullable=True)

    sample_size = Column(String(100), nullable=True)

    results = Column(Text, nullable=True)

    metrics = Column(Text, nullable=True)

    limitations = Column(Text, nullable=True)

    conclusion = Column(Text, nullable=True)

    evidence_text = Column(Text, nullable=True)

    evidence_location = Column(Text, nullable=True)

    extraction_confidence = Column(
        String(20),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    paper = relationship(
        "Paper",
        back_populates="extracted_data"
    )

class HumanFeedback(Base):
    __tablename__ = "human_feedback"

    id = Column(Integer, primary_key=True, index=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id"),
        nullable=False
    )

    original_decision = Column(
        String(30),
        nullable=True
    )

    corrected_decision = Column(
        String(30),
        nullable=True
    )

    feedback_text = Column(
        Text,
        nullable=True
    )

    reviewer_name = Column(
        String(150),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id = Column(Integer, primary_key=True, index=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    page_number = Column(
        Integer,
        nullable=False
    )

    chunk_text = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    paper = relationship(
        "Paper",
        back_populates="chunks"
    )

class EvidenceVerification(Base):
    __tablename__ = "evidence_verifications"

    id = Column(Integer, primary_key=True, index=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    claim = Column(Text, nullable=False)

    verification = Column(
        String(50),
        nullable=False
    )

    confidence = Column(
        String(20),
        nullable=True
    )

    explanation = Column(
        Text,
        nullable=True
    )

    evidence_text = Column(
        Text,
        nullable=True
    )

    evidence_location = Column(
        Text,
        nullable=True
    )

    ai_model = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    paper = relationship(
        "Paper",
        back_populates="evidence_verifications"
    )