from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum


class TransitionType(str, Enum):
    """Available transition types"""
    FADE = "fade"
    CROSSFADE = "crossfade"
    SLIDE = "slide"
    ZOOM = "zoom"
    WIPE = "wipe"
    DISSOLVE = "dissolve"


class VideoResolution(str, Enum):
    """Video resolution presets"""
    HD = "1920x1080"
    FULL_HD = "2560x1440"
    FOUR_K = "3840x2160"
    SD = "1280x720"
    MOBILE = "854x480"


class Scene(BaseModel):
    """Scene model for video rendering"""
    id: str = Field(..., description="Scene ID")
    image_path: str = Field(..., description="Path to scene image")
    audio_path: Optional[str] = Field(None, description="Path to scene audio")
    narration: str = Field(..., description="Scene narration text")
    duration: float = Field(..., ge=1.0, le=60.0, description="Scene duration in seconds")
    
    @validator('image_path')
    def validate_image_path(cls, v):
        if not v.strip():
            raise ValueError('Image path cannot be empty')
        return v.strip()
    
    @validator('narration')
    def validate_narration(cls, v):
        if not v.strip():
            raise ValueError('Narration cannot be empty')
        return v.strip()


class RenderVideoRequest(BaseModel):
    """Request model for video rendering"""
    scenes: List[Scene] = Field(..., min_length=1, description="List of scenes")
    output_filename: Optional[str] = Field(None, description="Custom output filename")
    fps: int = Field(default=30, ge=24, le=60, description="Frames per second")
    resolution: VideoResolution = Field(default=VideoResolution.HD, description="Video resolution")
    transition_type: TransitionType = Field(default=TransitionType.FADE, description="Transition type")
    transition_duration: float = Field(default=0.5, ge=0.1, le=2.0, description="Transition duration in seconds")
    add_subtitles: bool = Field(default=True, description="Add subtitles")
    background_music: Optional[str] = Field(None, description="Background music file path")
    
    @validator('output_filename')
    def validate_filename(cls, v):
        if v and not v.endswith('.mp4'):
            return f"{v}.mp4"
        return v


class RenderVideoResponse(BaseModel):
    """Response model for video rendering"""
    success: bool = Field(..., description="Rendering success status")
    video_file_path: str = Field(..., description="Path to rendered video file")
    total_duration: float = Field(..., description="Total video duration in seconds")
    total_scenes: int = Field(..., description="Number of scenes")
    file_size: Optional[int] = Field(None, description="Size of rendered file in bytes")
    rendering_time: Optional[float] = Field(None, description="Rendering time in seconds")
    video_info: Optional[Dict[str, Any]] = Field(None, description="Video metadata")


class VideoInfo(BaseModel):
    """Video information model"""
    duration: float = Field(..., description="Video duration in seconds")
    width: int = Field(..., description="Video width")
    height: int = Field(..., description="Video height")
    fps: float = Field(..., description="Frames per second")
    bitrate: Optional[int] = Field(None, description="Video bitrate")
    format: str = Field(..., description="Video format")
    size: int = Field(..., description="File size in bytes")


class RenderProgress(BaseModel):
    """Rendering progress model"""
    job_id: str = Field(..., description="Rendering job ID")
    status: str = Field(..., description="Current status")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    current_step: str = Field(..., description="Current rendering step")
    total_steps: int = Field(..., description="Total number of steps")
    current_scene: int = Field(..., description="Current scene being processed")
    total_scenes: int = Field(..., description="Total number of scenes")
    estimated_time_remaining: Optional[float] = Field(None, description="Estimated time remaining in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")


class DeleteVideoRequest(BaseModel):
    """Request model for deleting video files"""
    file_path: str = Field(..., description="Path to video file to delete")


class DeleteVideoResponse(BaseModel):
    """Response model for video deletion"""
    success: bool = Field(..., description="Deletion success status")
    file_path: str = Field(..., description="Path to deleted file")
    message: str = Field(..., description="Deletion message")


class CleanupVideosRequest(BaseModel):
    """Request model for cleanup operation"""
    max_age_hours: int = Field(default=24, ge=1, description="Maximum age of files to keep in hours")


class CleanupVideosResponse(BaseModel):
    """Response model for cleanup operation"""
    success: bool = Field(..., description="Cleanup success status")
    files_deleted: int = Field(..., description="Number of files deleted")
    max_age_hours: int = Field(..., description="Maximum age used for cleanup")
