from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VideoQuality(str, Enum):
    """Video quality options"""
    SD = "SD"
    HD = "HD"
    FULL_HD = "FULL_HD"
    UHD_4K = "UHD_4K"


class VideoStatus(str, Enum):
    """Video processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoFormat(str, Enum):
    """Video format options"""
    MP4 = "MP4"
    WEBM = "WEBM"
    AVI = "AVI"
    MOV = "MOV"


class VideoRequest(BaseModel):
    """Video generation request model"""
    script: str = Field(..., min_length=10, max_length=10000, description="The script for video generation")
    template_id: Optional[str] = Field(None, description="Template ID to use for video generation")
    quality: VideoQuality = Field(VideoQuality.HD, description="Video quality")
    format: VideoFormat = Field(VideoFormat.MP4, description="Video format")
    duration_limit: Optional[int] = Field(600, description="Maximum duration in seconds")
    style_preferences: Optional[Dict[str, Any]] = Field(None, description="Style preferences")


class VideoResponse(BaseModel):
    """Video response model"""
    id: str = Field(..., description="Video ID")
    script: str = Field(..., description="Original script")
    status: VideoStatus = Field(..., description="Video processing status")
    quality: VideoQuality = Field(..., description="Video quality")
    format: VideoFormat = Field(..., description="Video format")
    duration: Optional[int] = Field(None, description="Video duration in seconds")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    resolution: Optional[str] = Field(None, description="Video resolution")
    fps: Optional[int] = Field(None, description="Frames per second")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    video_url: Optional[str] = Field(None, description="Video URL")
    download_url: Optional[str] = Field(None, description="Download URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    processing_progress: Optional[int] = Field(None, description="Processing progress (0-100)")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class VideoStatusResponse(BaseModel):
    """Video status response model"""
    id: str = Field(..., description="Video ID")
    status: VideoStatus = Field(..., description="Video processing status")
    progress: Optional[int] = Field(None, description="Processing progress (0-100)")
    current_step: Optional[str] = Field(None, description="Current processing step")
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated time remaining in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class VideoListResponse(BaseModel):
    """Video list response model"""
    videos: List[VideoResponse] = Field(..., description="List of videos")
    total: int = Field(..., description="Total number of videos")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of videos per page")
    total_pages: int = Field(..., description="Total number of pages")


class VideoStats(BaseModel):
    """Video statistics model"""
    total_videos: int = Field(..., description="Total number of videos")
    completed_videos: int = Field(..., description="Number of completed videos")
    processing_videos: int = Field(..., description="Number of videos being processed")
    failed_videos: int = Field(..., description="Number of failed videos")
    total_duration: int = Field(..., description="Total duration of all videos in seconds")
    average_processing_time: Optional[float] = Field(None, description="Average processing time in seconds")
