from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from models.script_generation import (
    GenerateScriptRequest, GeneratedScriptResponse,
    SceneVariationRequest, EnhancePromptRequest,
    EnhancePromptResponse, ErrorResponse
)
from services.openai_service import get_openai_service
from services.database_service import get_database_service
from database.database import get_async_session, get_db
from routes.auth import get_current_active_user
from models.database import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate-script", response_model=GeneratedScriptResponse, status_code=status.HTTP_200_OK)
async def generate_script(
    request: GenerateScriptRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a complete video script using OpenAI API
    
    This endpoint takes a topic and description, then generates:
    - Title
    - Introduction
    - Scene-by-scene narration
    - Visual prompts for AI video generation
    - Scene durations
    - Conclusion
    
    Args:
        request: Script generation request with topic, description, and optional parameters
    
    Returns:
        GeneratedScriptResponse: Structured script data
    
    Raises:
        HTTPException: If script generation fails
    """
    try:
        logger.info(f"Generating script for topic: {request.topic}")
        
        openai_service = get_openai_service()
        db_service = get_database_service()
        
        # Generate script using OpenAI
        script_data = await openai_service.generate_script(
            topic=request.topic,
            description=request.description,
            num_scenes=request.num_scenes,
            style=request.style
        )
        
        # Create a project for the user
        project = await db_service.create_project(
            user_id=current_user.id,
            title=request.topic,
            description=request.description,
            topic=request.topic,
            settings={"style": request.style, "num_scenes": request.num_scenes}
        )
        
        # Create scenes in the database
        scenes = script_data.get('scenes', [])
        for i, scene_data in enumerate(scenes):
            await db_service.create_scene(
                project_id=project.id,
                scene_number=i + 1,
                narration=scene_data.get('narration', ''),
                visual_prompt=scene_data.get('visual_prompt', ''),
                duration=scene_data.get('duration', 5),
                camera_movement=scene_data.get('camera_movement', 'static'),
                mood=scene_data.get('mood', 'professional')
            )
        
        # Store the generated script as an asset
        await db_service.create_asset(
            project_id=project.id,
            asset_type='script',
            file_path=f"project_{project.id}/script.json",
            metadata=script_data,
            status='completed'
        )
        
        # Update project metadata
        await db_service.update_project_metadata(
            project_id=project.id,
            total_scenes=len(scenes)
        )
        
        logger.info(f"Script generated successfully with {len(scenes)} scenes for project {project.id}")
        
        return GeneratedScriptResponse(
            title=script_data.get('title', ''),
            introduction=script_data.get('introduction', ''),
            scenes=script_data.get('scenes', []),
            conclusion=script_data.get('conclusion', ''),
            estimated_duration=script_data.get('estimated_duration', 0),
            style=script_data.get('style', ''),
            raw_response=script_data.get('raw_response')
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate script: {str(e)}"
        )


@router.post("/generate-scene-variations")
async def generate_scene_variations(request: SceneVariationRequest):
    """
    Generate variations for a specific scene
    
    This endpoint takes a scene and generates multiple variations
    with different narration and visual prompts.
    
    Args:
        request: Scene variation request
    
    Returns:
        List of scene variations
    
    Raises:
        HTTPException: If variation generation fails
    """
    try:
        logger.info(f"Generating {request.variations} variations for scene {request.scene.scene_number}")
        
        openai_service = get_openai_service()
        
        variations = await openai_service.generate_scene_variations(
            scene=request.scene.dict(),
            variations=request.variations
        )
        
        logger.info(f"Successfully generated {len(variations)} scene variations")
        return {"variations": variations}
        
    except Exception as e:
        logger.error(f"Error generating scene variations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate variations: {str(e)}"
        )


@router.post("/enhance-visual-prompt", response_model=EnhancePromptResponse)
async def enhance_visual_prompt(request: EnhancePromptRequest):
    """
    Enhance a visual prompt with more detail and AI-specific terms
    
    This endpoint takes a basic visual prompt and enhances it with
    technical terms and details for better AI video generation results.
    
    Args:
        request: Visual prompt enhancement request
    
    Returns:
        Enhanced prompt response
    
    Raises:
        HTTPException: If prompt enhancement fails
    """
    try:
        logger.info("Enhancing visual prompt")
        
        openai_service = get_openai_service()
        
        enhanced_prompt = await openai_service.enhance_visual_prompt(
            visual_prompt=request.visual_prompt,
            style=request.style
        )
        
        logger.info("Successfully enhanced visual prompt")
        return EnhancePromptResponse(
            original_prompt=request.visual_prompt,
            enhanced_prompt=enhanced_prompt,
            style=request.style
        )
        
    except Exception as e:
        logger.error(f"Error enhancing visual prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance prompt: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for script generation service
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "script-generation",
        "openai_configured": bool(get_openai_service().settings.OPENAI_API_KEY)
    }
