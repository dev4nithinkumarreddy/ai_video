from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import logging

from models.script import (
    ScriptRequest, ScriptResponse, ScriptAnalysisRequest, 
    ScriptAnalysisResponse, ScriptTemplate
)
from services.script_service import ScriptService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=ScriptAnalysisResponse)
async def analyze_script(analysis_request: ScriptAnalysisRequest):
    """
    Analyze a script and return insights
    """
    try:
        script_service = ScriptService()
        analysis = await script_service.analyze_script(
            script=analysis_request.script,
            include_suggestions=analysis_request.include_suggestions,
            analysis_depth=analysis_request.analysis_depth
        )
        return analysis
    except Exception as e:
        logger.error(f"Failed to analyze script: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze script")


@router.post("/suggestions")
async def get_script_suggestions(script: str):
    """
    Get AI-powered suggestions for script improvement
    """
    try:
        script_service = ScriptService()
        suggestions = await script_service.get_script_suggestions(script)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Failed to get script suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get script suggestions")


@router.post("/", response_model=ScriptResponse)
async def save_script(script_request: ScriptRequest):
    """
    Save a script
    """
    try:
        script_service = ScriptService()
        script = await script_service.save_script(script_request)
        return script
    except Exception as e:
        logger.error(f"Failed to save script: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save script")


@router.get("/", response_model=List[ScriptResponse])
async def get_saved_scripts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """
    Get saved scripts with pagination and filtering
    """
    try:
        script_service = ScriptService()
        scripts = await script_service.get_saved_scripts(page=page, limit=limit, tag=tag)
        return scripts
    except Exception as e:
        logger.error(f"Failed to get saved scripts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get saved scripts")


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: str):
    """
    Get a saved script by ID
    """
    try:
        script_service = ScriptService()
        script = await script_service.get_script(script_id)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        return script
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get script")


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(script_id: str, script_request: ScriptRequest):
    """
    Update a saved script
    """
    try:
        script_service = ScriptService()
        script = await script_service.update_script(script_id, script_request)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        return script
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update script")


@router.delete("/{script_id}")
async def delete_script(script_id: str):
    """
    Delete a saved script
    """
    try:
        script_service = ScriptService()
        success = await script_service.delete_script(script_id)
        if not success:
            raise HTTPException(status_code=404, detail="Script not found")
        return {"message": "Script deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete script")


@router.get("/templates", response_model=List[ScriptTemplate])
async def get_script_templates(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get available script templates
    """
    try:
        script_service = ScriptService()
        templates = await script_service.get_script_templates(category=category)
        return templates
    except Exception as e:
        logger.error(f"Failed to get script templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get script templates")


@router.post("/templates/{template_id}/generate")
async def generate_script_from_template(
    template_id: str,
    variables: dict
):
    """
    Generate a script from a template
    """
    try:
        script_service = ScriptService()
        script = await script_service.generate_script_from_template(template_id, variables)
        if not script:
            raise HTTPException(status_code=404, detail="Template not found")
        return script
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate script from template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate script from template")
