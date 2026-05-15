from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
import logging
from pathlib import Path
import os
import time
import asyncio

from models.video_rendering import (
    RenderVideoRequest, RenderVideoResponse,
    VideoInfo, RenderProgress, DeleteVideoRequest,
    DeleteVideoResponse, CleanupVideosRequest,
    CleanupVideosResponse
)
from services.video_rendering_service import get_video_rendering_service

router = APIRouter()
logger = logging.getLogger(__name__)


# Progress tracking storage
_video_rendering_progress: dict = {}

# Queue for video rendering
_video_rendering_queue = asyncio.Queue()


@router.post("/render-video", response_model=RenderVideoResponse, status_code=status.HTTP_200_OK)
async def render_video(request: RenderVideoRequest):
    """
    Render a complete video from scenes using FFmpeg
    
    This endpoint combines scene images, adds narration audio, transitions,
    and subtitles to create a complete MP4 video.
    
    Args:
        request: Video rendering request with scenes and settings
    
    Returns:
        RenderVideoResponse: Path to rendered video file and metadata
    
    Raises:
        HTTPException: If video rendering fails
    """
    try:
        logger.info(f"Starting video rendering for {len(request.scenes)} scenes")
        
        video_service = get_video_rendering_service()
        
        # Convert scenes to dict format
        scenes_dict = [
            {
                "id": scene.id,
                "image_path": scene.image_path,
                "audio_path": scene.audio_path,
                "narration": scene.narration,
                "duration": scene.duration
            }
            for scene in request.scenes
        ]
        
        # Render video
        start_time = time.time()
        video_path = await video_service.render_video(
            scenes=scenes_dict,
            output_filename=request.output_filename,
            fps=request.fps,
            resolution=request.resolution.value,
            transition_type=request.transition_type.value,
            transition_duration=request.transition_duration,
            add_subtitles=request.add_subtitles,
            background_music=request.background_music
        )
        rendering_time = time.time() - start_time
        
        # Get file size
        file_size = os.path.getsize(video_path) if os.path.exists(video_path) else None
        
        # Get video info
        video_info = None
        try:
            video_info = await video_service.get_video_info(video_path)
        except Exception as e:
            logger.warning(f"Could not get video info: {str(e)}")
        
        # Calculate total duration
        total_duration = sum(scene.duration for scene in request.scenes)
        
        logger.info(f"Video rendering completed in {rendering_time:.2f}s: {video_path}")
        return RenderVideoResponse(
            success=True,
            video_file_path=video_path,
            total_duration=total_duration,
            total_scenes=len(request.scenes),
            file_size=file_size,
            rendering_time=rendering_time,
            video_info=video_info
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error rendering video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render video: {str(e)}"
        )


@router.post("/render-video-async")
async def render_video_async(
    background_tasks: BackgroundTasks,
    scenes: list[dict],
    output_filename: str = None,
    fps: int = 30,
    resolution: str = "1920x1080",
    transition_type: str = "fade",
    transition_duration: float = 0.5,
    add_subtitles: bool = True,
    background_music: str = None
):
    """
    Render video asynchronously with progress tracking
    
    This endpoint starts background video rendering and provides
    progress tracking via a job ID.
    
    Args:
        background_tasks: FastAPI background tasks
        scenes: Array of scene dictionaries
        output_filename: Optional custom filename
        fps: Frames per second
        resolution: Video resolution
        transition_type: Transition type
        transition_duration: Transition duration
        add_subtitles: Whether to add subtitles
        background_music: Optional background music
    
    Returns:
        JSON response with job ID for progress tracking
    """
    try:
        logger.info(f"Starting async video rendering for {len(scenes)} scenes")
        
        # Generate unique job ID
        import uuid
        job_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        _video_rendering_progress[job_id] = {
            "status": "processing",
            "progress_percentage": 0.0,
            "current_step": "Initializing",
            "total_steps": 6,  # Number of rendering steps
            "current_scene": 0,
            "total_scenes": len(scenes),
            "estimated_time_remaining": None,
            "error": None
        }
        
        # Start background task
        background_tasks.add_task(
            render_video_background,
            job_id,
            scenes,
            output_filename,
            fps,
            resolution,
            transition_type,
            transition_duration,
            add_subtitles,
            background_music
        )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "total_scenes": len(scenes),
            "message": "Video rendering started"
        }
        
    except Exception as e:
        logger.error(f"Error starting video rendering: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start video rendering: {str(e)}"
        )


async def render_video_background(
    job_id: str,
    scenes: list[dict],
    output_filename: str,
    fps: int,
    resolution: str,
    transition_type: str,
    transition_duration: float,
    add_subtitles: bool,
    background_music: str
):
    """
    Background task for video rendering with progress tracking
    
    Args:
        job_id: Unique job ID
        scenes: Array of scene dictionaries
        output_filename: Custom filename
        fps: Frames per second
        resolution: Video resolution
        transition_type: Transition type
        transition_duration: Transition duration
        add_subtitles: Whether to add subtitles
        background_music: Background music path
    """
    try:
        video_service = get_video_rendering_service()
        progress = _video_rendering_progress[job_id]
        
        def update_progress(step_name, percentage, current_scene=0):
            progress["current_step"] = step_name
            progress["progress_percentage"] = percentage
            progress["current_scene"] = current_scene
        
        # Step 1: Prepare scene videos
        update_progress("Preparing scene videos", 10.0)
        render_id = f"render_{int(time.time())}"
        temp_dir = video_service.temp_dir / render_id
        temp_dir.mkdir(exist_ok=True)
        
        scene_videos = []
        for i, scene in enumerate(scenes):
            try:
                image_path = scene.get('image_path')
                duration = scene.get('duration', 5)
                
                if not image_path or not os.path.exists(image_path):
                    logger.warning(f"Image not found for scene {i}: {image_path}")
                    continue
                
                scene_video_path = temp_dir / f"scene_{i}.mp4"
                await video_service._create_scene_video(
                    image_path, scene_video_path, duration, fps, resolution
                )
                scene_videos.append(str(scene_video_path))
                
                # Update progress for scene preparation
                scene_progress = 10.0 + (40.0 * (i + 1) / len(scenes))
                update_progress("Preparing scene videos", scene_progress, i + 1)
                
            except Exception as e:
                logger.error(f"Error preparing scene video {i}: {str(e)}")
                continue
        
        # Step 2: Create concatenation list
        update_progress("Creating video sequence", 55.0)
        concat_list = temp_dir / "concat_list.txt"
        with open(concat_list, 'w') as f:
            for video_path in scene_videos:
                f.write(f"file '{video_path}'\n")
                f.write(f"duration {transition_duration}\n")
        
        # Step 3: Concatenate scenes
        update_progress("Combining scenes", 65.0)
        temp_video_path = temp_dir / "concatenated_video.mp4"
        await video_service._concatenate_videos(str(concat_list), temp_video_path)
        
        # Step 4: Add audio
        update_progress("Adding audio", 75.0)
        temp_audio_path = temp_dir / "with_audio.mp4"
        await video_service._add_audio_to_video(
            temp_video_path, scenes, temp_audio_path, background_music
        )
        
        # Step 5: Add subtitles
        temp_with_subtitles_path = temp_dir / "with_subtitles.mp4"
        if add_subtitles:
            update_progress("Adding subtitles", 85.0)
            await video_service._add_subtitles_to_video(
                temp_audio_path, scenes, temp_with_subtitles_path
            )
            final_temp_path = temp_with_subtitles_path
        else:
            final_temp_path = temp_audio_path
        
        # Step 6: Finalize video
        update_progress("Finalizing video", 95.0)
        if not output_filename:
            output_filename = f"video_{int(time.time())}.mp4"
        final_path = video_service.video_dir / output_filename
        os.rename(final_temp_path, final_path)
        
        # Cleanup
        await video_service._cleanup_temp_files(temp_dir)
        
        # Update final status
        progress["status"] = "completed"
        progress["progress_percentage"] = 100.0
        progress["current_step"] = "Completed"
        progress["video_file_path"] = str(final_path)
        
        logger.info(f"Video rendering job {job_id} completed: {final_path}")
        
    except Exception as e:
        logger.error(f"Video rendering job {job_id} failed: {str(e)}")
        progress = _video_rendering_progress[job_id]
        progress["status"] = "failed"
        progress["error"] = str(e)


@router.get("/render-video-async/{job_id}")
async def get_video_rendering_progress(job_id: str):
    """
    Get progress of video rendering job
    
    Args:
        job_id: Job ID returned from render-video-async
    
    Returns:
        Progress information including video path when complete
    """
    if job_id not in _video_rendering_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job ID not found: {job_id}"
        )
    
    progress = _video_rendering_progress[job_id]
    return progress


@router.post("/generate-video")
async def generate_video(
    background_tasks: BackgroundTasks,
    scenes: list[dict],
    images: list[str],
    audio_files: list[str],
    output_filename: str = None,
    fps: int = 30,
    resolution: str = "1920x1080",
    transition_type: str = "fade",
    transition_duration: float = 0.5,
    add_subtitles: bool = True,
    background_music: str = None
):
    """
    Generate video from scenes, images, and audio with queue processing
    
    This endpoint accepts scenes with associated images and audio files,
    triggers FFmpeg rendering, and provides status updates for long processing tasks.
    
    Args:
        background_tasks: FastAPI background tasks
        scenes: Array of scene dictionaries with narration and duration
        images: Array of image file paths corresponding to scenes
        audio_files: Array of audio file paths corresponding to scenes
        output_filename: Optional custom output filename
        fps: Frames per second
        resolution: Video resolution
        transition_type: Transition type between scenes
        transition_duration: Duration of transitions
        add_subtitles: Whether to add subtitles
        background_music: Optional background music file path
    
    Returns:
        JSON response with job ID for progress tracking
    """
    try:
        logger.info(f"Queueing video generation for {len(scenes)} scenes")
        
        # Validate input
        if len(scenes) != len(images):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of scenes must match number of images"
            )
        
        if len(audio_files) > 0 and len(audio_files) != len(scenes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of audio files must match number of scenes"
            )
        
        # Generate unique job ID
        import uuid
        job_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        _video_rendering_progress[job_id] = {
            "status": "queued",
            "progress_percentage": 0.0,
            "current_step": "Queued for processing",
            "total_steps": 8,  # Number of processing steps
            "current_scene": 0,
            "total_scenes": len(scenes),
            "estimated_time_remaining": None,
            "error": None,
            "queue_position": _video_rendering_queue.qsize()
        }
        
        # Prepare scene data with images and audio
        scene_data = []
        for i, scene in enumerate(scenes):
            scene_dict = {
                "id": scene.get('id', f"scene_{i}"),
                "narration": scene.get('narration', ''),
                "duration": scene.get('duration', 5),
                "image_path": images[i] if i < len(images) else None,
                "audio_path": audio_files[i] if i < len(audio_files) and len(audio_files) > 0 else None
            }
            scene_data.append(scene_dict)
        
        # Add job to queue
        await _video_rendering_queue.put({
            "job_id": job_id,
            "scenes": scene_data,
            "output_filename": output_filename,
            "fps": fps,
            "resolution": resolution,
            "transition_type": transition_type,
            "transition_duration": transition_duration,
            "add_subtitles": add_subtitles,
            "background_music": background_music
        })
        
        # Start background queue processor if not running
        background_tasks.add_task(process_video_rendering_queue)
        
        return {
            "job_id": job_id,
            "status": "queued",
            "total_scenes": len(scenes),
            "queue_position": _video_rendering_queue.qsize(),
            "message": "Video generation queued for processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queueing video generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue video generation: {str(e)}"
        )


async def process_video_rendering_queue():
    """
    Background task to process video rendering queue
    """
    logger.info("Starting video rendering queue processor")
    
    while True:
        try:
            # Get job from queue
            job_data = await _video_rendering_queue.get()
            job_id = job_data["job_id"]
            
            logger.info(f"Processing video generation job {job_id} from queue")
            
            # Update status to processing
            if job_id in _video_rendering_progress:
                _video_rendering_progress[job_id]["status"] = "processing"
                _video_rendering_progress[job_id]["queue_position"] = 0
            
            # Process the job
            await process_video_generation_job(job_data)
            
            # Mark queue item as done
            _video_rendering_queue.task_done()
            
        except Exception as e:
            logger.error(f"Error processing video rendering queue item: {str(e)}")
            await asyncio.sleep(1)


async def process_video_generation_job(job_data: dict):
    """
    Process a single video generation job
    
    Args:
        job_data: Job data with all rendering parameters
    """
    job_id = job_data["job_id"]
    
    try:
        video_service = get_video_rendering_service()
        
        if job_id not in _video_rendering_progress:
            logger.warning(f"Job {job_id} not found in progress tracking")
            return
        
        progress = _video_rendering_progress[job_id]
        
        def update_progress(step_name, percentage, current_scene=0):
            progress["current_step"] = step_name
            progress["progress_percentage"] = percentage
            progress["current_scene"] = current_scene
        
        # Step 1: Validate inputs
        update_progress("Validating inputs", 5.0)
        scenes = job_data["scenes"]
        
        # Step 2: Prepare scene videos
        update_progress("Preparing scene videos", 10.0)
        render_id = f"render_{int(time.time())}"
        temp_dir = video_service.temp_dir / render_id
        temp_dir.mkdir(exist_ok=True)
        
        scene_videos = []
        for i, scene in enumerate(scenes):
            try:
                image_path = scene.get('image_path')
                duration = scene.get('duration', 5)
                
                if not image_path or not os.path.exists(image_path):
                    logger.warning(f"Image not found for scene {i}: {image_path}")
                    continue
                
                scene_video_path = temp_dir / f"scene_{i}.mp4"
                await video_service._create_scene_video(
                    image_path, scene_video_path, duration, 
                    job_data["fps"], job_data["resolution"]
                )
                scene_videos.append(str(scene_video_path))
                
                # Update progress for scene preparation
                scene_progress = 10.0 + (30.0 * (i + 1) / len(scenes))
                update_progress("Preparing scene videos", scene_progress, i + 1)
                
            except Exception as e:
                logger.error(f"Error preparing scene video {i}: {str(e)}")
                continue
        
        # Step 3: Create concatenation list
        update_progress("Creating video sequence", 45.0)
        concat_list = temp_dir / "concat_list.txt"
        with open(concat_list, 'w') as f:
            for video_path in scene_videos:
                f.write(f"file '{video_path}'\n")
                f.write(f"duration {job_data['transition_duration']}\n")
        
        # Step 4: Concatenate scenes
        update_progress("Combining scenes", 55.0)
        temp_video_path = temp_dir / "concatenated_video.mp4"
        await video_service._concatenate_videos(str(concat_list), temp_video_path)
        
        # Step 5: Add audio
        update_progress("Adding audio", 65.0)
        temp_audio_path = temp_dir / "with_audio.mp4"
        await video_service._add_audio_to_video(
            temp_video_path, scenes, temp_audio_path, job_data["background_music"]
        )
        
        # Step 6: Add subtitles
        temp_with_subtitles_path = temp_dir / "with_subtitles.mp4"
        if job_data["add_subtitles"]:
            update_progress("Adding subtitles", 75.0)
            await video_service._add_subtitles_to_video(
                temp_audio_path, scenes, temp_with_subtitles_path
            )
            final_temp_path = temp_with_subtitles_path
        else:
            final_temp_path = temp_audio_path
        
        # Step 7: Finalize video
        update_progress("Finalizing video", 85.0)
        output_filename = job_data["output_filename"]
        if not output_filename:
            output_filename = f"video_{int(time.time())}.mp4"
        final_path = video_service.video_dir / output_filename
        os.rename(final_temp_path, final_path)
        
        # Step 8: Cleanup
        update_progress("Cleaning up temporary files", 95.0)
        await video_service._cleanup_temp_files(temp_dir)
        
        # Update final status
        progress["status"] = "completed"
        progress["progress_percentage"] = 100.0
        progress["current_step"] = "Completed"
        progress["video_file_path"] = str(final_path)
        progress["video_url"] = f"/api/video-rendering/video/{output_filename}"
        
        logger.info(f"Video generation job {job_id} completed: {final_path}")
        
    except Exception as e:
        logger.error(f"Video generation job {job_id} failed: {str(e)}")
        if job_id in _video_rendering_progress:
            progress = _video_rendering_progress[job_id]
            progress["status"] = "failed"
            progress["error"] = str(e)


@router.get("/generate-video/{job_id}")
async def get_video_generation_progress(job_id: str):
    """
    Get progress of video generation job
    
    Args:
        job_id: Job ID returned from generate-video
    
    Returns:
        Progress information including video URL when complete
    """
    if job_id not in _video_rendering_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job ID not found: {job_id}"
        )
    
    progress = _video_rendering_progress[job_id]
    return progress


@router.get("/video/{filename}")
async def get_video_file(filename: str):
    """
    Download a video file
    
    Args:
        filename: Name of the video file to download
    
    Returns:
        FileResponse: Video file
    
    Raises:
        HTTPException: If file not found
    """
    try:
        video_service = get_video_rendering_service()
        file_path = video_service.video_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video file not found: {filename}"
            )
        
        return FileResponse(
            path=file_path,
            media_type="video/mp4",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving video file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve video file: {str(e)}"
        )


@router.get("/video/{filename}/info")
async def get_video_info(filename: str):
    """
    Get video information
    
    Args:
        filename: Name of the video file
    
    Returns:
        Video information
    
    Raises:
        HTTPException: If file not found or info retrieval fails
    """
    try:
        video_service = get_video_rendering_service()
        file_path = video_service.video_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video file not found: {filename}"
            )
        
        info = await video_service.get_video_info(str(file_path))
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get video info: {str(e)}"
        )


@router.delete("/video", response_model=DeleteVideoResponse, status_code=status.HTTP_200_OK)
async def delete_video_file(request: DeleteVideoRequest):
    """
    Delete a video file
    
    Args:
        request: Delete video request with file path
    
    Returns:
        DeleteVideoResponse: Deletion status
    
    Raises:
        HTTPException: If deletion fails
    """
    try:
        logger.info(f"Deleting video file: {request.file_path}")
        
        file_path = Path(request.file_path)
        if not file_path.exists():
            return DeleteVideoResponse(
                success=False,
                file_path=request.file_path,
                message="Video file not found"
            )
        
        file_path.unlink()
        logger.info(f"Deleted video file: {request.file_path}")
        
        return DeleteVideoResponse(
            success=True,
            file_path=request.file_path,
            message="Video file deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting video file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete video file: {str(e)}"
        )


@router.post("/cleanup", response_model=CleanupVideosResponse, status_code=status.HTTP_200_OK)
async def cleanup_old_videos(request: CleanupVideosRequest):
    """
    Clean up old video files
    
    This endpoint deletes video files older than the specified age.
    
    Args:
        request: Cleanup request with max age in hours
    
    Returns:
        CleanupVideosResponse: Cleanup status and count of deleted files
    
    Raises:
        HTTPException: If cleanup fails
    """
    try:
        logger.info(f"Cleaning up video files older than {request.max_age_hours} hours")
        
        video_service = get_video_rendering_service()
        deleted_count = 0
        current_time = time.time()
        max_age_seconds = request.max_age_hours * 3600
        
        for file_path in video_service.video_dir.glob("*.mp4"):
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                file_path.unlink()
                deleted_count += 1
                logger.info(f"Deleted old video file: {file_path.name}")
        
        logger.info(f"Cleanup complete: {deleted_count} files deleted")
        return CleanupVideosResponse(
            success=True,
            files_deleted=deleted_count,
            max_age_hours=request.max_age_hours
        )
        
    except Exception as e:
        logger.error(f"Error cleaning up video files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup video files: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for video rendering service
    
    Returns:
        Health status
    """
    try:
        video_service = get_video_rendering_service()
        health = await video_service.health_check()
        return health
    except Exception as e:
        logger.error(f"Video rendering health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
