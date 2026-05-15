from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import logging
from pathlib import Path
import os
from typing import Dict, Optional
import asyncio

from models.audio import (
    GenerateAudioRequest, GenerateAudioWithSettingsRequest,
    GenerateSceneAudioRequest, GenerateAudioResponse,
    GenerateSceneAudioResponse, VoicesResponse,
    DeleteAudioRequest, DeleteAudioResponse,
    CleanupRequest, CleanupResponse
)
from services.audio_service import get_audio_service

router = APIRouter()
logger = logging.getLogger(__name__)


# Progress tracking storage
_audio_generation_progress: Dict[str, Dict] = {}


@router.post("/generate-audio", response_model=GenerateAudioResponse, status_code=status.HTTP_200_OK)
async def generate_audio(request: GenerateAudioRequest):
    """
    Generate audio from text using ElevenLabs API
    
    This endpoint converts text to speech using the ElevenLabs API
    and saves the generated audio file to the generated/audio directory.
    
    Args:
        request: Audio generation request with text and optional voice settings
    
    Returns:
        GenerateAudioResponse: Path to generated audio file and metadata
    
    Raises:
        HTTPException: If audio generation fails
    """
    try:
        logger.info(f"Generating audio for text length: {len(request.text)}")
        
        audio_service = get_audio_service()
        
        # Generate audio
        audio_path = await audio_service.generate_audio(
            text=request.text,
            voice_id=request.voice_id,
            model_id=request.model_id.value,
            output_filename=request.output_filename
        )
        
        # Get file size
        file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else None
        
        logger.info(f"Audio generated successfully: {audio_path}")
        return GenerateAudioResponse(
            success=True,
            audio_file_path=audio_path,
            voice_id=request.voice_id,
            model_id=request.model_id.value,
            text_length=len(request.text),
            file_size=file_size
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate audio: {str(e)}"
        )


@router.post("/generate-audio-with-settings", response_model=GenerateAudioResponse, status_code=status.HTTP_200_OK)
async def generate_audio_with_settings(request: GenerateAudioWithSettingsRequest):
    """
    Generate audio with custom voice settings
    
    This endpoint converts text to speech using ElevenLabs API with
    custom voice settings for stability, similarity boost, and style.
    
    Args:
        request: Audio generation request with custom voice settings
    
    Returns:
        GenerateAudioResponse: Path to generated audio file and metadata
    
    Raises:
        HTTPException: If audio generation fails
    """
    try:
        logger.info(f"Generating audio with custom settings")
        
        audio_service = get_audio_service()
        
        # Generate audio with settings
        audio_path = await audio_service.generate_audio_with_settings(
            text=request.text,
            voice_id=request.voice_id,
            model_id=request.model_id.value,
            stability=request.settings.stability,
            similarity_boost=request.settings.similarity_boost,
            style=request.settings.style,
            use_speaker_boost=request.settings.use_speaker_boost,
            output_filename=request.output_filename
        )
        
        # Get file size
        file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else None
        
        logger.info(f"Audio generated with settings: {audio_path}")
        return GenerateAudioResponse(
            success=True,
            audio_file_path=audio_path,
            voice_id=request.voice_id,
            model_id=request.model_id.value,
            text_length=len(request.text),
            file_size=file_size
        )
        
    except Exception as e:
        logger.error(f"Error generating audio with settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate audio with settings: {str(e)}"
        )


@router.post("/generate-scene-audio", response_model=GenerateSceneAudioResponse, status_code=status.HTTP_200_OK)
async def generate_scene_audio(request: GenerateSceneAudioRequest):
    """
    Generate audio for multiple scenes
    
    This endpoint batch processes multiple scenes and generates
    audio files for each scene's narration.
    
    Args:
        request: Scene audio generation request with list of scenes
    
    Returns:
        GenerateSceneAudioResponse: Mapping of scene IDs to audio file paths
    
    Raises:
        HTTPException: If audio generation fails
    """
    try:
        logger.info(f"Generating audio for {len(request.scenes)} scenes")
        
        audio_service = get_audio_service()
        
        # Convert scenes to dict format
        scenes_dict = [
            {
                "id": scene.id,
                "narration": scene.narration
            }
            for scene in request.scenes
        ]
        
        # Generate audio for all scenes
        audio_files = await audio_service.generate_scene_audio(
            scenes=scenes_dict,
            voice_id=request.voice_id,
            model_id=request.model_id.value
        )
        
        # Count successful and failed generations
        successful = len([f for f in audio_files.values() if f])
        failed = len([f for f in audio_files.values() if not f])
        
        logger.info(f"Scene audio generation complete: {successful}/{len(request.scenes)} successful")
        return GenerateSceneAudioResponse(
            success=successful > 0,
            audio_files=audio_files,
            total_scenes=len(request.scenes),
            successful_generations=successful,
            failed_generations=failed
        )
        
    except Exception as e:
        logger.error(f"Error generating scene audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate scene audio: {str(e)}"
        )


@router.post("/generate-audio-scenes")
async def generate_audio_scenes(
    background_tasks: BackgroundTasks,
    narrations: list[str],
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = "eleven_multilingual_v2"
):
    """
    Generate audio for scene narrations with progress tracking
    
    This endpoint accepts an array of scene narrations, generates voice for each,
    returns audio URLs, tracks progress, and handles failures gracefully.
    
    Args:
        background_tasks: FastAPI background tasks
        narrations: Array of scene narration texts
        voice_id: ElevenLabs voice ID
        model_id: ElevenLabs model ID
    
    Returns:
        JSON response with generation ID for progress tracking
    """
    try:
        logger.info(f"Starting audio generation for {len(narrations)} scenes")
        
        # Generate unique generation ID
        import uuid
        generation_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        _audio_generation_progress[generation_id] = {
            "status": "processing",
            "total_scenes": len(narrations),
            "completed_scenes": 0,
            "failed_scenes": 0,
            "audio_urls": {},
            "errors": {},
            "current_scene": 0
        }
        
        # Start background task for audio generation
        background_tasks.add_task(
            generate_audio_background,
            generation_id,
            narrations,
            voice_id,
            model_id
        )
        
        return {
            "generation_id": generation_id,
            "status": "processing",
            "total_scenes": len(narrations),
            "message": "Audio generation started"
        }
        
    except Exception as e:
        logger.error(f"Error starting audio generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start audio generation: {str(e)}"
        )


async def generate_audio_background(
    generation_id: str,
    narrations: list[str],
    voice_id: str,
    model_id: str
):
    """
    Background task for audio generation with progress tracking
    
    Args:
        generation_id: Unique generation ID
        narrations: Array of scene narrations
        voice_id: ElevenLabs voice ID
        model_id: ElevenLabs model ID
    """
    try:
        audio_service = get_audio_service()
        progress = _audio_generation_progress[generation_id]
        
        for index, narration in enumerate(narrations):
            try:
                progress["current_scene"] = index + 1
                
                if not narration or not narration.strip():
                    logger.warning(f"Scene {index + 1} has empty narration, skipping")
                    progress["failed_scenes"] += 1
                    progress["errors"][str(index)] = "Empty narration"
                    continue
                
                # Generate audio for this scene
                output_filename = f"scene_{index + 1}_{generation_id}.mp3"
                audio_path = await audio_service.generate_audio(
                    text=narration,
                    voice_id=voice_id,
                    model_id=model_id,
                    output_filename=output_filename
                )
                
                # Convert file path to URL
                audio_url = f"/api/audio/audio/{output_filename}"
                progress["audio_urls"][str(index)] = audio_url
                progress["completed_scenes"] += 1
                
                logger.info(f"Generated audio for scene {index + 1}: {audio_url}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to generate audio for scene {index + 1}: {str(e)}")
                progress["failed_scenes"] += 1
                progress["errors"][str(index)] = str(e)
        
        # Update final status
        progress["status"] = "completed"
        logger.info(f"Audio generation {generation_id} completed: {progress['completed_scenes']}/{len(narrations)} successful")
        
    except Exception as e:
        logger.error(f"Background audio generation failed: {str(e)}")
        _audio_generation_progress[generation_id]["status"] = "failed"
        _audio_generation_progress[generation_id]["error"] = str(e)


@router.get("/generate-audio-scenes/{generation_id}")
async def get_audio_generation_progress(generation_id: str):
    """
    Get progress of audio generation
    
    Args:
        generation_id: Generation ID returned from generate-audio-scenes
    
    Returns:
        Progress information including audio URLs
    """
    if generation_id not in _audio_generation_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation ID not found: {generation_id}"
        )
    
    progress = _audio_generation_progress[generation_id]
    return progress


@router.get("/voices", response_model=VoicesResponse, status_code=status.HTTP_200_OK)
async def get_voices():
    """
    Get list of available voices from ElevenLabs
    
    Returns:
        VoicesResponse: List of available voices
    
    Raises:
        HTTPException: If fetching voices fails
    """
    try:
        logger.info("Fetching available voices")
        
        audio_service = get_audio_service()
        voices = await audio_service.get_available_voices()
        
        logger.info(f"Retrieved {len(voices)} voices")
        return VoicesResponse(
            voices=voices,
            total_count=len(voices)
        )
        
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch voices: {str(e)}"
        )


@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """
    Download an audio file
    
    Args:
        filename: Name of the audio file to download
    
    Returns:
        FileResponse: Audio file
    
    Raises:
        HTTPException: If file not found
    """
    try:
        audio_service = get_audio_service()
        file_path = audio_service.audio_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {filename}"
            )
        
        return FileResponse(
            path=file_path,
            media_type="audio/mpeg",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving audio file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve audio file: {str(e)}"
        )


@router.delete("/audio", response_model=DeleteAudioResponse, status_code=status.HTTP_200_OK)
async def delete_audio_file(request: DeleteAudioRequest):
    """
    Delete an audio file
    
    Args:
        request: Delete audio request with file path
    
    Returns:
        DeleteAudioResponse: Deletion status
    
    Raises:
        HTTPException: If deletion fails
    """
    try:
        logger.info(f"Deleting audio file: {request.file_path}")
        
        audio_service = get_audio_service()
        success = await audio_service.delete_audio_file(request.file_path)
        
        if success:
            return DeleteAudioResponse(
                success=True,
                file_path=request.file_path,
                message="Audio file deleted successfully"
            )
        else:
            return DeleteAudioResponse(
                success=False,
                file_path=request.file_path,
                message="Audio file not found or could not be deleted"
            )
        
    except Exception as e:
        logger.error(f"Error deleting audio file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete audio file: {str(e)}"
        )


@router.post("/cleanup", response_model=CleanupResponse, status_code=status.HTTP_200_OK)
async def cleanup_old_audio_files(request: CleanupRequest):
    """
    Clean up old audio files
    
    This endpoint deletes audio files older than the specified age.
    
    Args:
        request: Cleanup request with max age in hours
    
    Returns:
        CleanupResponse: Cleanup status and count of deleted files
    
    Raises:
        HTTPException: If cleanup fails
    """
    try:
        logger.info(f"Cleaning up audio files older than {request.max_age_hours} hours")
        
        audio_service = get_audio_service()
        deleted_count = await audio_service.cleanup_old_audio_files(request.max_age_hours)
        
        logger.info(f"Cleanup complete: {deleted_count} files deleted")
        return CleanupResponse(
            success=True,
            files_deleted=deleted_count,
            max_age_hours=request.max_age_hours
        )
        
    except Exception as e:
        logger.error(f"Error cleaning up audio files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup audio files: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for audio generation service
    
    Returns:
        Health status
    """
    try:
        audio_service = get_audio_service()
        health = await audio_service.health_check()
        return health
    except Exception as e:
        logger.error(f"Audio health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
