from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum


class ValidationStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    category_breakdown = Column(JSON, nullable=True)

    total_activities = Column(Integer, nullable=False)
    invisible_work_score = Column(Float, nullable=False)
    
    # Category breakdown
    mentoring = Column(Integer, default=0)
    knowledge_sharing = Column(Integer, default=0)
    documentation = Column(Integer, default=0)
    incident_support = Column(Integer, default=0)
    meetings = Column(Integer, default=0)
    cross_team_collaboration = Column(Integer, default=0)
    process_improvement = Column(Integer, default=0)
    administrative_work = Column(Integer, default=0)
    
    # Recognition Gap Analysis
    recognition_gap_score = Column(Integer, nullable=False)
    recognition_gap_explanation = Column(Text, nullable=False)
    recognition_gap_recommendations = Column(Text, nullable=False)
    
    # Impact Analysis
    impact_score = Column(Integer, nullable=False)
    impact_explanation = Column(Text, nullable=False)
    top_impact_drivers = Column(Text, nullable=False)
    
    # AI Insights (stored as JSON string)
    ai_insights = Column(JSON, nullable=True)
    
    # Performance Summary
    performance_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContributionValidation(Base):
    __tablename__ = "contribution_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    contribution_text = Column(Text, nullable=False)
    validator_name = Column(String(255), nullable=False)
    status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Made with Bob
