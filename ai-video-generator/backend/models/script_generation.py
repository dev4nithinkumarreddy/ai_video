from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class ScriptStyle(str, Enum):
    """Script style options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CINEMATIC = "cinematic"
    EDUCATIONAL = "educational"
    MARKETING = "marketing"
    STORYTELLING = "storytelling"


class CameraMovement(str, Enum):
    """Camera movement options"""
    STATIC = "static"
    PAN = "pan"
    ZOOM = "zoom"
    TILT = "tilt"
    TRACK = "track"
    DOLLY = "dolly"
    HANDHELD = "handheld"


class GenerateScriptRequest(BaseModel):
    """Request model for script generation"""
    topic: str = Field(..., min_length=3, max_length=200, description="Video topic")
    description: str = Field(..., min_length=10, max_length=5000, description="Video description")
    num_scenes: int = Field(default=3, ge=1, le=10, description="Number of scenes to generate")
    style: ScriptStyle = Field(default=ScriptStyle.PROFESSIONAL, description="Script style")
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v.strip():
            raise ValueError('Topic cannot be empty or whitespace only')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip()


class Scene(BaseModel):
    """Scene model"""
    scene_number: int = Field(..., ge=1, description="Scene number")
    narration: str = Field(..., min_length=10, description="Scene narration")
    visual_prompt: str = Field(..., min_length=10, description="Visual prompt for AI generation")
    duration: int = Field(..., ge=2, le=30, description="Scene duration in seconds")
    camera_movement: CameraMovement = Field(default=CameraMovement.STATIC, description="Camera movement")


class GeneratedScriptResponse(BaseModel):
    """Response model for generated script"""
    title: str = Field(..., description="Video title")
    introduction: str = Field(..., description="Script introduction")
    scenes: List[Scene] = Field(..., description="List of scenes")
    conclusion: str = Field(..., description="Script conclusion")
    estimated_duration: int = Field(..., ge=1, description="Estimated total duration in seconds")
    style: str = Field(..., description="Script style used")
    raw_response: Optional[str] = Field(None, description="Raw AI response if parsing failed")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


class SceneVariationRequest(BaseModel):
    """Request model for scene variations"""
    scene: Scene = Field(..., description="Original scene")
    variations: int = Field(default=3, ge=1, le=5, description="Number of variations to generate")


class EnhancePromptRequest(BaseModel):
    """Request model for visual prompt enhancement"""
    visual_prompt: str = Field(..., min_length=5, description="Original visual prompt")
    style: str = Field(default="cinematic", description="Enhancement style")


class EnhancePromptResponse(BaseModel):
    """Response model for enhanced prompt"""
    original_prompt: str = Field(..., description="Original visual prompt")
    enhanced_prompt: str = Field(..., description="Enhanced visual prompt")
    style: str = Field(..., description="Style used for enhancement")
