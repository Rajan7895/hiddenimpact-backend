from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class CategoryBreakdown(BaseModel):
    """Schema for category breakdown"""
    mentoring: int = Field(default=0, ge=0)
    knowledge_sharing: int = Field(default=0, ge=0)
    documentation: int = Field(default=0, ge=0)
    incident_support: int = Field(default=0, ge=0)
    meetings: int = Field(default=0, ge=0)
    cross_team_collaboration: int = Field(default=0, ge=0)
    process_improvement: int = Field(default=0, ge=0)
    administrative_work: int = Field(default=0, ge=0)


class RecognitionGapAnalysis(BaseModel):
    """Schema for recognition gap analysis"""
    score: int = Field(ge=0, le=100, description="Recognition Gap Score (0-100)")
    explanation: str = Field(description="Explanation of why the score was assigned")
    recommendations: str = Field(description="Recommendations for highlighting contributions")


class ImpactAnalysis(BaseModel):
    """Schema for impact analysis"""
    score: int = Field(ge=0, le=100, description="Impact Score (0-100)")
    explanation: str = Field(description="Explanation of organizational value created")
    top_drivers: str = Field(description="Top impact drivers")

class AIInsights(BaseModel):
    """Schema for AI-generated insights"""
    top_hidden_contributions: list[Dict[str, str]] = Field(description="Most valuable invisible work activities")
    leadership_indicators: Dict[str, str] = Field(description="Leadership qualities demonstrated")
    collaboration_strengths: Dict[str, str] = Field(description="Collaboration and team enablement strengths")
    burnout_indicators: Dict[str, str] = Field(description="Potential burnout risk factors")
    performance_review_highlights: list[str] = Field(description="Ready-to-use performance review bullet points")



class AnalysisResult(BaseModel):
    """Schema for analysis results"""
    category_breakdown: CategoryBreakdown
    invisible_work_score: float = Field(ge=0.0, le=1.0)
    recognition_gap_analysis: RecognitionGapAnalysis
    impact_analysis: ImpactAnalysis
    ai_insights: AIInsights
    performance_summary: str
    total_activities: int = Field(ge=0)


class AnalysisResponse(BaseModel):
    """Schema for API response"""
    id: int
    filename: str
    file_type: str
    category_breakdown: Dict[str, int]
    invisible_work_score: float
    recognition_gap_score: int
    recognition_gap_explanation: str
    recognition_gap_recommendations: str
    impact_score: int
    impact_explanation: str
    top_impact_drivers: str
    ai_insights: Dict
    performance_summary: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """Schema for list of analyses"""
    total: int
    analyses: list[AnalysisResponse]


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str

# Contribution Validation Schemas

class ContributionValidationCreate(BaseModel):
    """Schema for creating a contribution validation"""
    analysis_id: int = Field(description="ID of the analysis this validation belongs to")
    contribution_text: str = Field(description="The contribution text to validate")
    validator_name: str = Field(description="Name of the person validating")
    notes: Optional[str] = Field(default=None, description="Optional notes about the validation")


class ContributionValidationUpdate(BaseModel):
    """Schema for updating a contribution validation"""
    status: str = Field(description="Status: pending, approved, or rejected")
    notes: Optional[str] = Field(default=None, description="Optional notes about the validation")


class ContributionValidationResponse(BaseModel):
    """Schema for contribution validation response"""
    id: int
    analysis_id: int
    contribution_text: str
    validator_name: str
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ValidationConfidenceScore(BaseModel):
    """Schema for validation confidence score"""
    confidence_score: float = Field(ge=0.0, le=100.0, description="Confidence score (0-100)")
    total_validations: int = Field(description="Total number of validations")
    approved_count: int = Field(description="Number of approved validations")
    rejected_count: int = Field(description="Number of rejected validations")
    pending_count: int = Field(description="Number of pending validations")


# Made with Bob
