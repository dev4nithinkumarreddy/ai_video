import asyncio
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from models.video import (
    VideoRequest, VideoResponse, VideoStatusResponse, 
    VideoListResponse, VideoStats, VideoQuality, VideoFormat, VideoStatus
)
from utils.config import get_settings

logger = logging.getLogger(__name__)

# In-memory storage for demo purposes (replace with database in production)
videos_db: Dict[str, Dict[str, Any]] = {}


class VideoService:
    """Service for video operations"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def create_video(self, video_request: VideoRequest) -> VideoResponse:
        """Create a new video generation request"""
        video_id = str(uuid.uuid4())
        
        video_data = {
            "id": video_id,
            "script": video_request.script,
            "template_id": video_request.template_id,
            "status": VideoStatus.PENDING,
            "quality": video_request.quality,
            "format": video_request.format,
            "duration_limit": video_request.duration_limit,
            "style_preferences": video_request.style_preferences or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "processing_progress": 0,
            "duration": None,
            "file_size": None,
            "resolution": None,
            "fps": None,
            "thumbnail_url": None,
            "video_url": None,
            "download_url": None,
            "error_message": None
        }
        
        videos_db[video_id] = video_data
        
        # Start video processing in background
        asyncio.create_task(self._process_video(video_id))
        
        return VideoResponse(**video_data)
    
    async def get_video(self, video_id: str) -> Optional[VideoResponse]:
        """Get video by ID"""
        video_data = videos_db.get(video_id)
        if not video_data:
            return None
        return VideoResponse(**video_data)
    
    async def get_video_status(self, video_id: str) -> Optional[VideoStatusResponse]:
        """Get video processing status"""
        video_data = videos_db.get(video_id)
        if not video_data:
            return None
        
        return VideoStatusResponse(
            id=video_id,
            status=video_data["status"],
            progress=video_data.get("processing_progress"),
            current_step=video_data.get("current_step"),
            estimated_time_remaining=video_data.get("estimated_time_remaining"),
            error_message=video_data.get("error_message")
        )
    
    async def get_videos(
        self, 
        page: int = 1, 
        limit: int = 10, 
        status: Optional[str] = None,
        quality: Optional[VideoQuality] = None
    ) -> VideoListResponse:
        """Get list of videos with pagination and filtering"""
        filtered_videos = []
        
        for video_data in videos_db.values():
            if status and video_data["status"] != status:
                continue
            if quality and video_data["quality"] != quality:
                continue
            filtered_videos.append(VideoResponse(**video_data))
        
        # Sort by created_at descending
        filtered_videos.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_videos = filtered_videos[start:end]
        
        total = len(filtered_videos)
        total_pages = (total + limit - 1) // limit
        
        return VideoListResponse(
            videos=paginated_videos,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    async def download_video(self, video_id: str, quality: VideoQuality) -> Optional[bytes]:
        """Download video file"""
        video_data = videos_db.get(video_id)
        if not video_data or video_data["status"] != VideoStatus.COMPLETED:
            return None
        
        # In a real implementation, this would return the actual video file
        # For demo purposes, return a placeholder
        return b"placeholder video content"
    
    async def delete_video(self, video_id: str) -> bool:
        """Delete a video"""
        if video_id not in videos_db:
            return False
        
        del videos_db[video_id]
        return True
    
    async def get_video_stats(self) -> VideoStats:
        """Get video statistics"""
        total_videos = len(videos_db)
        completed_videos = sum(1 for v in videos_db.values() if v["status"] == VideoStatus.COMPLETED)
        processing_videos = sum(1 for v in videos_db.values() if v["status"] == VideoStatus.PROCESSING)
        failed_videos = sum(1 for v in videos_db.values() if v["status"] == VideoStatus.FAILED)
        
        # Calculate total duration and average processing time
        total_duration = sum(v.get("duration", 0) for v in videos_db.values() if v.get("duration"))
        avg_processing_time = None  # Would calculate from actual processing times
        
        return VideoStats(
            total_videos=total_videos,
            completed_videos=completed_videos,
            processing_videos=processing_videos,
            failed_videos=failed_videos,
            total_duration=total_duration,
            average_processing_time=avg_processing_time
        )
    
    async def retry_video(self, video_id: str) -> Optional[VideoResponse]:
        """Retry failed video processing"""
        video_data = videos_db.get(video_id)
        if not video_data:
            return None
        
        # Reset status and start processing again
        video_data["status"] = VideoStatus.PENDING
        video_data["processing_progress"] = 0
        video_data["error_message"] = None
        video_data["updated_at"] = datetime.utcnow()
        
        # Start processing in background
        asyncio.create_task(self._process_video(video_id))
        
        return VideoResponse(**video_data)
    
    async def _process_video(self, video_id: str):
        """Background task to process video"""
        video_data = videos_db.get(video_id)
        if not video_data:
            return
        
        processing_steps = [
            "Analyzing script",
            "Generating scenes",
            "Creating visuals",
            "Adding animations",
            "Processing audio",
            "Finalizing video"
        ]
        
        try:
            # Update status to processing
            video_data["status"] = VideoStatus.PROCESSING
            video_data["updated_at"] = datetime.utcnow()
            
            # Simulate processing steps
            for i, step in enumerate(processing_steps):
                video_data["current_step"] = step
                video_data["processing_progress"] = int((i + 1) / len(processing_steps) * 100)
                video_data["estimated_time_remaining"] = max(5, 45 - video_data["processing_progress"])
                video_data["updated_at"] = datetime.utcnow()
                
                # Simulate processing time
                await asyncio.sleep(2)
            
            # Mark as completed
            video_data["status"] = VideoStatus.COMPLETED
            video_data["processing_progress"] = 100
            video_data["duration"] = 165  # 2:45 in seconds
            video_data["file_size"] = 47420800  # ~45MB
            video_data["resolution"] = "1920x1080"
            video_data["fps"] = 30
            video_data["video_url"] = f"/api/videos/{video_id}/stream"
            video_data["download_url"] = f"/api/videos/{video_id}/download"
            video_data["current_step"] = None
            video_data["estimated_time_remaining"] = None
            video_data["updated_at"] = datetime.utcnow()
            
            logger.info(f"Video {video_id} processing completed")
            
        except Exception as e:
            logger.error(f"Video {video_id} processing failed: {str(e)}")
            video_data["status"] = VideoStatus.FAILED
            video_data["error_message"] = str(e)
            video_data["updated_at"] = datetime.utcnow()
