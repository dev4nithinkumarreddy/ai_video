from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScriptAnalysis(BaseModel):
    """Script analysis result model"""
    word_count: int = Field(..., description="Number of words in the script")
    character_count: int = Field(..., description="Number of characters in the script")
    estimated_duration: int = Field(..., description="Estimated duration in seconds")
    sentiment: Optional[str] = Field(None, description="Sentiment analysis result")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    topics: List[str] = Field(default_factory=list, description="Detected topics")
    complexity_score: Optional[float] = Field(None, description="Complexity score (0-1)")
    readability_score: Optional[float] = Field(None, description="Readability score")


class ScriptSuggestion(BaseModel):
    """Script suggestion model"""
    type: str = Field(..., description="Type of suggestion")
    text: str = Field(..., description="Suggestion text")
    priority: str = Field(..., description="Priority level (low, medium, high)")
    original_text: Optional[str] = Field(None, description="Original text to modify")
    suggested_text: Optional[str] = Field(None, description="Suggested replacement text")


class ScriptRequest(BaseModel):
    """Script request model"""
    script: str = Field(..., min_length=10, max_length=10000, description="The script content")
    title: Optional[str] = Field(None, description="Script title")
    description: Optional[str] = Field(None, description="Script description")
    tags: List[str] = Field(default_factory=list, description="Script tags")


class ScriptResponse(BaseModel):
    """Script response model"""
    id: str = Field(..., description="Script ID")
    title: Optional[str] = Field(None, description="Script title")
    description: Optional[str] = Field(None, description="Script description")
    script: str = Field(..., description="Script content")
    tags: List[str] = Field(default_factory=list, description="Script tags")
    analysis: Optional[ScriptAnalysis] = Field(None, description="Script analysis")
    suggestions: Optional[List[ScriptSuggestion]] = Field(default_factory=list, description="AI suggestions")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ScriptAnalysisRequest(BaseModel):
    """Script analysis request model"""
    script: str = Field(..., min_length=10, max_length=10000, description="Script to analyze")
    include_suggestions: bool = Field(True, description="Include AI suggestions")
    analysis_depth: str = Field("standard", description="Analysis depth (basic, standard, advanced)")


class ScriptAnalysisResponse(BaseModel):
    """Script analysis response model"""
    analysis: ScriptAnalysis = Field(..., description="Script analysis result")
    suggestions: Optional[List[ScriptSuggestion]] = Field(None, description="AI suggestions")
    processing_time: float = Field(..., description="Processing time in seconds")


class ScriptTemplate(BaseModel):
    """Script template model"""
    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    script_template: str = Field(..., description="Script template with placeholders")
    variables: List[str] = Field(..., description="List of variables in the template")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    created_at: datetime = Field(..., description="Creation timestamp")
