from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List
import logging
import asyncio
from datetime import datetime

from models.video import (
    VideoRequest, VideoResponse, VideoStatusResponse, 
    VideoListResponse, VideoStats, VideoQuality, VideoFormat
)
from services.video_service import VideoService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=VideoResponse)
async def create_video(video_request: VideoRequest):
    """
    Create a new video generation request
    """
    try:
        video_service = VideoService()
        video = await video_service.create_video(video_request)
        return video
    except Exception as e:
        logger.error(f"Failed to create video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create video")


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """
    Get video details by ID
    """
    try:
        video_service = VideoService()
        video = await video_service.get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return video
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get video")


@router.get("/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(video_id: str):
    """
    Get video processing status
    """
    try:
        video_service = VideoService()
        status = await video_service.get_video_status(video_id)
        if not status:
            raise HTTPException(status_code=404, detail="Video not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video status {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get video status")


@router.get("/", response_model=VideoListResponse)
async def get_videos(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    quality: Optional[VideoQuality] = Query(None, description="Filter by quality")
):
    """
    Get list of videos with pagination and filtering
    """
    try:
        video_service = VideoService()
        videos = await video_service.get_videos(page=page, limit=limit, status=status, quality=quality)
        return videos
    except Exception as e:
        logger.error(f"Failed to get videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get videos")


@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    quality: Optional[VideoQuality] = Query(VideoQuality.HD, description="Video quality")
):
    """
    Download video file
    """
    try:
        video_service = VideoService()
        video_stream = await video_service.download_video(video_id, quality)
        if not video_stream:
            raise HTTPException(status_code=404, detail="Video not found")
        
        filename = f"video_{video_id}_{quality.value.lower()}.mp4"
        return StreamingResponse(
            video_stream,
            media_type="video/mp4",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download video")


@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """
    Delete a video
    """
    try:
        video_service = VideoService()
        success = await video_service.delete_video(video_id)
        if not success:
            raise HTTPException(status_code=404, detail="Video not found")
        return {"message": "Video deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete video")


@router.get("/stats", response_model=VideoStats)
async def get_video_stats():
    """
    Get video statistics
    """
    try:
        video_service = VideoService()
        stats = await video_service.get_video_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get video stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get video stats")


@router.post("/{video_id}/retry")
async def retry_video(video_id: str):
    """
    Retry failed video processing
    """
    try:
        video_service = VideoService()
        video = await video_service.retry_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return video
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retry video")
