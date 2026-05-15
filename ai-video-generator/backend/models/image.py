from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum


class ImageModel(str, Enum):
    """Available image generation models"""
    SDXL = "stability-ai/sdxl"
    STABLE_DIFFUSION = "stability-ai/stable-diffusion"
    MIDJOURNEY = "midjourney"


class ImageQuality(str, Enum):
    """Image quality presets"""
    HD = "HD"
    FULL_HD = "FULL_HD"
    FOUR_K = "FOUR_K"


class GenerateImageRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., min_length=10, max_length=1000, description="Image generation prompt")
    model: ImageModel = Field(default=ImageModel.SDXL, description="AI model to use")
    width: int = Field(default=1920, ge=512, le=2048, description="Image width in pixels")
    height: int = Field(default=1080, ge=512, le=2048, description="Image height in pixels")
    quality: ImageQuality = Field(default=ImageQuality.HD, description="Image quality preset")
    output_filename: Optional[str] = Field(None, description="Custom output filename")
    num_inference_steps: int = Field(default=50, ge=10, le=100, description="Number of inference steps")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="Guidance scale for prompt adherence")
    negative_prompt: Optional[str] = Field(None, max_length=500, description="Negative prompt")
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty or whitespace only')
        return v.strip()
    
    @validator('output_filename')
    def validate_filename(cls, v):
        if v and not v.endswith('.png'):
            return f"{v}.png"
        return v
    
    @validator('quality')
    def apply_quality_preset(cls, v, values):
        quality_map = {
            ImageQuality.HD: (1920, 1080),
            ImageQuality.FULL_HD: (2560, 1440),
            ImageQuality.FOUR_K: (3840, 2160)
        }
        if v in quality_map:
            width, height = quality_map[v]
            # Only set if not explicitly provided
            if 'width' not in values or values['width'] == 1920:
                values['width'] = width
            if 'height' not in values or values['height'] == 1080:
                values['height'] = height
        return v


class Scene(BaseModel):
    """Scene model for batch image generation"""
    id: str = Field(..., description="Scene ID")
    visual_prompt: str = Field(..., min_length=10, max_length=1000, description="Visual description for image")
    
    @validator('visual_prompt')
    def validate_visual_prompt(cls, v):
        if not v.strip():
            raise ValueError('Visual prompt cannot be empty or whitespace only')
        return v.strip()


class GenerateSceneImagesRequest(BaseModel):
    """Request model for batch scene image generation"""
    scenes: List[Scene] = Field(..., min_length=1, description="List of scenes")
    model: ImageModel = Field(default=ImageModel.SDXL, description="AI model to use")
    quality: ImageQuality = Field(default=ImageQuality.HD, description="Image quality preset")
    negative_prompt: Optional[str] = Field(None, max_length=500, description="Negative prompt for all images")


class GenerateImageResponse(BaseModel):
    """Response model for image generation"""
    success: bool = Field(..., description="Generation success status")
    image_file_path: str = Field(..., description="Path to generated image file")
    model_used: str = Field(..., description="Model used for generation")
    prompt_length: int = Field(..., description="Length of input prompt")
    file_size: Optional[int] = Field(None, description="Size of generated file in bytes")
    generation_time: Optional[float] = Field(None, description="Generation time in seconds")


class GenerateSceneImagesResponse(BaseModel):
    """Response model for batch scene image generation"""
    success: bool = Field(..., description="Overall success status")
    image_files: Dict[str, Optional[str]] = Field(..., description="Scene ID to image file path mapping")
    total_scenes: int = Field(..., description="Total number of scenes")
    successful_generations: int = Field(..., description="Number of successful generations")
    failed_generations: int = Field(..., description="Number of failed generations")


class DeleteImageRequest(BaseModel):
    """Request model for deleting image files"""
    file_path: str = Field(..., description="Path to image file to delete")


class DeleteImageResponse(BaseModel):
    """Response model for image deletion"""
    success: bool = Field(..., description="Deletion success status")
    file_path: str = Field(..., description="Path to deleted file")
    message: str = Field(..., description="Deletion message")


class CleanupImagesRequest(BaseModel):
    """Request model for cleanup operation"""
    max_age_hours: int = Field(default=24, ge=1, description="Maximum age of files to keep in hours")


class CleanupImagesResponse(BaseModel):
    """Response model for cleanup operation"""
    success: bool = Field(..., description="Cleanup success status")
    files_deleted: int = Field(..., description="Number of files deleted")
    max_age_hours: int = Field(..., description="Maximum age used for cleanup")
