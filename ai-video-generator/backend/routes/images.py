import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from models.image import (
    GenerateImageRequest, GenerateSceneImagesRequest,
    GenerateImageResponse, GenerateSceneImagesResponse,
    DeleteImageRequest, DeleteImageResponse,
    CleanupImagesRequest, CleanupImagesResponse
)
from services.image_service import get_image_service

router = APIRouter()
logger = logging.getLogger(__name__)


# Progress tracking storage
_image_generation_progress: dict = {}

# Queue for image generation
_image_queue = asyncio.Queue()


@router.post("/generate-image", response_model=GenerateImageResponse, status_code=status.HTTP_200_OK)
async def generate_image(request: GenerateImageRequest):
    """
    Generate a cinematic image using Replicate API
    
    This endpoint generates high-quality images from text prompts using
    state-of-the-art AI models like Stable Diffusion XL.
    
    Args:
        request: Image generation request with prompt and settings
    
    Returns:
        GenerateImageResponse: Path to generated image file and metadata
    
    Raises:
        HTTPException: If image generation fails
    """
    try:
        logger.info(f"Generating image with prompt length: {len(request.prompt)}")
        
        image_service = get_image_service()
        
        # Generate image
        start_time = time.time()
        image_path = await image_service.generate_image(
            prompt=request.prompt,
            model=request.model.value,
            width=request.width,
            height=request.height,
            output_filename=request.output_filename,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            negative_prompt=request.negative_prompt
        )
        generation_time = time.time() - start_time
        
        # Get file size
        file_size = os.path.getsize(image_path) if os.path.exists(image_path) else None
        
        logger.info(f"Image generated successfully in {generation_time:.2f}s: {image_path}")
        return GenerateImageResponse(
            success=True,
            image_file_path=image_path,
            model_used=request.model.value,
            prompt_length=len(request.prompt),
            file_size=file_size,
            generation_time=generation_time
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}"
        )


@router.post("/generate-scene-images", response_model=GenerateSceneImagesResponse, status_code=status.HTTP_200_OK)
async def generate_scene_images(request: GenerateSceneImagesRequest):
    """
    Generate images for multiple scenes
    
    This endpoint batch processes multiple scenes and generates
    cinematic images for each scene's visual prompt.
    
    Args:
        request: Scene image generation request with list of scenes
    
    Returns:
        GenerateSceneImagesResponse: Mapping of scene IDs to image file paths
    
    Raises:
        HTTPException: If image generation fails
    """
    try:
        logger.info(f"Generating images for {len(request.scenes)} scenes")
        
        image_service = get_image_service()
        
        # Convert scenes to dict format
        scenes_dict = [
            {
                "id": scene.id,
                "visualPrompt": scene.visual_prompt
            }
            for scene in request.scenes
        ]
        
        # Apply quality preset
        quality_map = {
            "HD": (1920, 1080),
            "FULL_HD": (2560, 1440),
            "FOUR_K": (3840, 2160)
        }
        width, height = quality_map.get(request.quality.value, (1920, 1080))
        
        # Generate images for all scenes
        image_files = await image_service.generate_scene_images(
            scenes=scenes_dict,
            model=request.model.value,
            width=width,
            height=height,
            negative_prompt=request.negative_prompt
        )
        
        # Count successful and failed generations
        successful = len([f for f in image_files.values() if f])
        failed = len([f for f in image_files.values() if not f])
        
        logger.info(f"Scene image generation complete: {successful}/{len(request.scenes)} successful")
        return GenerateSceneImagesResponse(
            success=successful > 0,
            image_files=image_files,
            total_scenes=len(request.scenes),
            successful_generations=successful,
            failed_generations=failed
        )
        
    except Exception as e:
        logger.error(f"Error generating scene images: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate scene images: {str(e)}"
        )


@router.post("/generate-scene-images-async")
async def generate_scene_images_async(
    background_tasks: BackgroundTasks,
    scenes: list[dict],
    model: str = "stability-ai/sdxl",
    quality: str = "HD",
    negative_prompt: str = None
):
    """
    Generate images for scenes asynchronously with progress tracking
    
    This endpoint starts background image generation for multiple scenes
    and provides progress tracking via a generation ID.
    
    Args:
        background_tasks: FastAPI background tasks
        scenes: Array of scene dictionaries with id and visualPrompt
        model: AI model to use
        quality: Image quality preset
        negative_prompt: Optional negative prompt
    
    Returns:
        JSON response with generation ID for progress tracking
    """
    try:
        logger.info(f"Starting async image generation for {len(scenes)} scenes")
        
        # Generate unique generation ID
        import uuid
        generation_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        _image_generation_progress[generation_id] = {
            "status": "processing",
            "total_scenes": len(scenes),
            "completed_scenes": 0,
            "failed_scenes": 0,
            "image_urls": {},
            "errors": {},
            "current_scene": 0
        }
        
        # Apply quality preset
        quality_map = {
            "HD": (1920, 1080),
            "FULL_HD": (2560, 1440),
            "FOUR_K": (3840, 2160)
        }
        width, height = quality_map.get(quality, (1920, 1080))
        
        # Start background task
        background_tasks.add_task(
            generate_scene_images_background,
            generation_id,
            scenes,
            model,
            width,
            height,
            negative_prompt
        )
        
        return {
            "generation_id": generation_id,
            "status": "processing",
            "total_scenes": len(scenes),
            "message": "Image generation started"
        }
        
    except Exception as e:
        logger.error(f"Error starting image generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start image generation: {str(e)}"
        )


async def generate_scene_images_background(
    generation_id: str,
    scenes: list[dict],
    model: str,
    width: int,
    height: int,
    negative_prompt: str
):
    """
    Background task for scene image generation with progress tracking
    
    Args:
        generation_id: Unique generation ID
        scenes: Array of scene dictionaries
        model: AI model to use
        width: Image width
        height: Image height
        negative_prompt: Optional negative prompt
    """
    try:
        image_service = get_image_service()
        progress = _image_generation_progress[generation_id]
        
        for index, scene in enumerate(scenes):
            try:
                progress["current_scene"] = index + 1
                scene_id = scene.get('id')
                visual_prompt = scene.get('visualPrompt', scene.get('visual_prompt', ''))
                
                if not visual_prompt or not visual_prompt.strip():
                    logger.warning(f"Scene {scene_id} has empty visual prompt, skipping")
                    progress["failed_scenes"] += 1
                    progress["errors"][str(index)] = "Empty visual prompt"
                    continue
                
                # Generate image for this scene
                output_filename = f"scene_{scene_id}_{generation_id}.png"
                image_path = await image_service.generate_image(
                    prompt=visual_prompt,
                    model=model,
                    width=width,
                    height=height,
                    output_filename=output_filename,
                    negative_prompt=negative_prompt
                )
                
                # Convert file path to URL
                image_url = f"/api/images/image/{output_filename}"
                progress["image_urls"][str(index)] = image_url
                progress["completed_scenes"] += 1
                
                logger.info(f"Generated image for scene {scene_id}: {image_url}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to generate image for scene {index}: {str(e)}")
                progress["failed_scenes"] += 1
                progress["errors"][str(index)] = str(e)
        
        # Update final status
        progress["status"] = "completed"
        logger.info(f"Image generation {generation_id} completed: {progress['completed_scenes']}/{len(scenes)} successful")
        
    except Exception as e:
        logger.error(f"Background image generation failed: {str(e)}")
        _image_generation_progress[generation_id]["status"] = "failed"
        _image_generation_progress[generation_id]["error"] = str(e)


@router.get("/generate-scene-images-async/{generation_id}")
async def get_image_generation_progress(generation_id: str):
    """
    Get progress of image generation
    
    Args:
        generation_id: Generation ID returned from generate-scene-images-async
    
    Returns:
        Progress information including image URLs
    """
    if generation_id not in _image_generation_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation ID not found: {generation_id}"
        )
    
    progress = _image_generation_progress[generation_id]
    return progress


@router.post("/generate-images")
async def generate_images(
    background_tasks: BackgroundTasks,
    prompts: list[str],
    model: str = "stability-ai/sdxl",
    quality: str = "HD",
    negative_prompt: str = None
):
    """
    Generate images from scene prompts with queue processing
    
    This endpoint accepts an array of scene prompts, generates images for each,
    returns image URLs, tracks progress, and handles queue processing.
    
    Args:
        background_tasks: FastAPI background tasks
        prompts: Array of scene prompt texts
        model: AI model to use
        quality: Image quality preset
        negative_prompt: Optional negative prompt
    
    Returns:
        JSON response with job ID for progress tracking
    """
    try:
        logger.info(f"Queueing image generation for {len(prompts)} scenes")
        
        # Generate unique job ID
        import uuid
        job_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        _image_generation_progress[job_id] = {
            "status": "queued",
            "total_scenes": len(prompts),
            "completed_scenes": 0,
            "failed_scenes": 0,
            "image_urls": {},
            "errors": {},
            "current_scene": 0,
            "queue_position": _image_queue.qsize()
        }
        
        # Apply quality preset
        quality_map = {
            "HD": (1920, 1080),
            "FULL_HD": (2560, 1440),
            "FOUR_K": (3840, 2160)
        }
        width, height = quality_map.get(quality, (1920, 1080))
        
        # Add job to queue
        await _image_queue.put({
            "job_id": job_id,
            "prompts": prompts,
            "model": model,
            "width": width,
            "height": height,
            "negative_prompt": negative_prompt
        })
        
        # Start background queue processor if not running
        background_tasks.add_task(process_image_queue)
        
        return {
            "job_id": job_id,
            "status": "queued",
            "total_scenes": len(prompts),
            "queue_position": _image_queue.qsize(),
            "message": "Image generation queued"
        }
        
    except Exception as e:
        logger.error(f"Error queueing image generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue image generation: {str(e)}"
        )


async def process_image_queue():
    """
    Background task to process image generation queue
    """
    logger.info("Starting image queue processor")
    
    while True:
        try:
            # Get job from queue
            job_data = await _image_queue.get()
            job_id = job_data["job_id"]
            
            logger.info(f"Processing job {job_id} from queue")
            
            # Update status to processing
            if job_id in _image_generation_progress:
                _image_generation_progress[job_id]["status"] = "processing"
                _image_generation_progress[job_id]["queue_position"] = 0
            
            # Process the job
            await process_image_job(
                job_id,
                job_data["prompts"],
                job_data["model"],
                job_data["width"],
                job_data["height"],
                job_data["negative_prompt"]
            )
            
            # Mark queue item as done
            _image_queue.task_done()
            
        except Exception as e:
            logger.error(f"Error processing queue item: {str(e)}")
            await asyncio.sleep(1)


async def process_image_job(
    job_id: str,
    prompts: list[str],
    model: str,
    width: int,
    height: int,
    negative_prompt: str
):
    """
    Process a single image generation job
    
    Args:
        job_id: Job ID
        prompts: Array of prompts
        model: AI model
        width: Image width
        height: Image height
        negative_prompt: Optional negative prompt
    """
    try:
        image_service = get_image_service()
        
        if job_id not in _image_generation_progress:
            logger.warning(f"Job {job_id} not found in progress tracking")
            return
        
        progress = _image_generation_progress[job_id]
        
        for index, prompt in enumerate(prompts):
            try:
                progress["current_scene"] = index + 1
                
                if not prompt or not prompt.strip():
                    logger.warning(f"Scene {index + 1} has empty prompt, skipping")
                    progress["failed_scenes"] += 1
                    progress["errors"][str(index)] = "Empty prompt"
                    continue
                
                # Generate image for this scene
                output_filename = f"scene_{index + 1}_{job_id}.png"
                image_path = await image_service.generate_image(
                    prompt=prompt,
                    model=model,
                    width=width,
                    height=height,
                    output_filename=output_filename,
                    negative_prompt=negative_prompt
                )
                
                # Convert file path to URL
                image_url = f"/api/images/image/{output_filename}"
                progress["image_urls"][str(index)] = image_url
                progress["completed_scenes"] += 1
                
                logger.info(f"Generated image for scene {index + 1}: {image_url}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to generate image for scene {index}: {str(e)}")
                progress["failed_scenes"] += 1
                progress["errors"][str(index)] = str(e)
        
        # Update final status
        progress["status"] = "completed"
        logger.info(f"Image generation job {job_id} completed: {progress['completed_scenes']}/{len(prompts)} successful")
        
    except Exception as e:
        logger.error(f"Image generation job {job_id} failed: {str(e)}")
        if job_id in _image_generation_progress:
            _image_generation_progress[job_id]["status"] = "failed"
            _image_generation_progress[job_id]["error"] = str(e)


@router.get("/generate-images/{job_id}")
async def get_image_job_progress(job_id: str):
    """
    Get progress of image generation job
    
    Args:
        job_id: Job ID returned from generate-images
    
    Returns:
        Progress information including image URLs
    """
    if job_id not in _image_generation_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job ID not found: {job_id}"
        )
    
    progress = _image_generation_progress[job_id]
    return progress


@router.get("/image/{filename}")
async def get_image_file(filename: str):
    """
    Download an image file
    
    Args:
        filename: Name of the image file to download
    
    Returns:
        FileResponse: Image file
    
    Raises:
        HTTPException: If file not found
    """
    try:
        image_service = get_image_service()
        file_path = image_service.image_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found: {filename}"
            )
        
        return FileResponse(
            path=file_path,
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve image file: {str(e)}"
        )


@router.delete("/image", response_model=DeleteImageResponse, status_code=status.HTTP_200_OK)
async def delete_image_file(request: DeleteImageRequest):
    """
    Delete an image file
    
    Args:
        request: Delete image request with file path
    
    Returns:
        DeleteImageResponse: Deletion status
    
    Raises:
        HTTPException: If deletion fails
    """
    try:
        logger.info(f"Deleting image file: {request.file_path}")
        
        image_service = get_image_service()
        success = await image_service.delete_image_file(request.file_path)
        
        if success:
            return DeleteImageResponse(
                success=True,
                file_path=request.file_path,
                message="Image file deleted successfully"
            )
        else:
            return DeleteImageResponse(
                success=False,
                file_path=request.file_path,
                message="Image file not found or could not be deleted"
            )
        
    except Exception as e:
        logger.error(f"Error deleting image file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image file: {str(e)}"
        )


@router.post("/cleanup", response_model=CleanupImagesResponse, status_code=status.HTTP_200_OK)
async def cleanup_old_images(request: CleanupImagesRequest):
    """
    Clean up old image files
    
    This endpoint deletes image files older than the specified age.
    
    Args:
        request: Cleanup request with max age in hours
    
    Returns:
        CleanupImagesResponse: Cleanup status and count of deleted files
    
    Raises:
        HTTPException: If cleanup fails
    """
    try:
        logger.info(f"Cleaning up image files older than {request.max_age_hours} hours")
        
        image_service = get_image_service()
        deleted_count = await image_service.cleanup_old_images(request.max_age_hours)
        
        logger.info(f"Cleanup complete: {deleted_count} files deleted")
        return CleanupImagesResponse(
            success=True,
            files_deleted=deleted_count,
            max_age_hours=request.max_age_hours
        )
        
    except Exception as e:
        logger.error(f"Error cleaning up image files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup image files: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for image generation service
    
    Returns:
        Health status
    """
    try:
        image_service = get_image_service()
        health = await image_service.health_check()
        return health
    except Exception as e:
        logger.error(f"Image health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
