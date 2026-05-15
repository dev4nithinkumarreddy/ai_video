from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TemplateCategory(str, Enum):
    """Template category options"""
    CORPORATE = "corporate"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    MARKETING = "marketing"
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    TUTORIAL = "tutorial"
    STORYTELLING = "storytelling"


class TemplateStyle(BaseModel):
    """Template style configuration"""
    color_scheme: List[str] = Field(..., description="Color palette")
    font_family: str = Field(..., description="Font family")
    background_style: str = Field(..., description="Background style")
    animation_style: str = Field(..., description="Animation style")
    transition_effects: List[str] = Field(default_factory=list, description="Transition effects")


class TemplateSettings(BaseModel):
    """Template settings"""
    max_duration: int = Field(..., description="Maximum duration in seconds")
    default_quality: str = Field("HD", description="Default quality")
    supported_formats: List[str] = Field(default_factory=lambda: ["MP4", "WebM"], description="Supported formats")
    aspect_ratio: str = Field("16:9", description="Aspect ratio")
    fps: int = Field(30, description="Frames per second")


class Template(BaseModel):
    """Video template model"""
    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: TemplateCategory = Field(..., description="Template category")
    style: TemplateStyle = Field(..., description="Template style configuration")
    settings: TemplateSettings = Field(..., description="Template settings")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    preview_url: Optional[str] = Field(None, description="Preview video URL")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    popularity_score: float = Field(0.0, description="Popularity score")
    usage_count: int = Field(0, description="Number of times used")
    is_premium: bool = Field(False, description="Whether template is premium")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TemplateRequest(BaseModel):
    """Template creation request model"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str = Field(..., min_length=10, max_length=500, description="Template description")
    category: TemplateCategory = Field(..., description="Template category")
    style: TemplateStyle = Field(..., description="Template style configuration")
    settings: TemplateSettings = Field(..., description="Template settings")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    is_premium: bool = Field(False, description="Whether template is premium")


class TemplateResponse(BaseModel):
    """Template response model"""
    template: Template = Field(..., description="Template details")


class TemplateListResponse(BaseModel):
    """Template list response model"""
    templates: List[Template] = Field(..., description="List of templates")
    total: int = Field(..., description="Total number of templates")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of templates per page")
    total_pages: int = Field(..., description="Total number of pages")
    categories: List[TemplateCategory] = Field(..., description="Available categories")


class TemplateUsage(BaseModel):
    """Template usage statistics"""
    template_id: str = Field(..., description="Template ID")
    usage_count: int = Field(..., description="Number of times used")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    user_ratings: List[float] = Field(default_factory=list, description="User ratings")
    average_rating: Optional[float] = Field(None, description="Average rating")
