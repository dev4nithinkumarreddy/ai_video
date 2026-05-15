from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import logging

from models.template import (
    Template, TemplateRequest, TemplateResponse, 
    TemplateListResponse, TemplateCategory, TemplateUsage
)
from services.template_service import TemplateService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=TemplateListResponse)
async def get_templates(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[TemplateCategory] = Query(None, description="Filter by category"),
    is_premium: Optional[bool] = Query(None, description="Filter by premium status"),
    search: Optional[str] = Query(None, description="Search templates")
):
    """
    Get list of templates with pagination and filtering
    """
    try:
        template_service = TemplateService()
        templates = await template_service.get_templates(
            page=page, 
            limit=limit, 
            category=category, 
            is_premium=is_premium, 
            search=search
        )
        return templates
    except Exception as e:
        logger.error(f"Failed to get templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


@router.get("/categories", response_model=List[TemplateCategory])
async def get_template_categories():
    """
    Get available template categories
    """
    try:
        template_service = TemplateService()
        categories = await template_service.get_categories()
        return categories
    except Exception as e:
        logger.error(f"Failed to get template categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get template categories")


@router.get("/popular", response_model=List[Template])
async def get_popular_templates(
    limit: int = Query(10, ge=1, le=50, description="Number of templates to return")
):
    """
    Get popular templates based on usage and ratings
    """
    try:
        template_service = TemplateService()
        templates = await template_service.get_popular_templates(limit=limit)
        return templates
    except Exception as e:
        logger.error(f"Failed to get popular templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get popular templates")


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """
    Get template details by ID
    """
    try:
        template_service = TemplateService()
        template = await template_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get template")


@router.post("/", response_model=TemplateResponse)
async def create_template(template_request: TemplateRequest):
    """
    Create a new template
    """
    try:
        template_service = TemplateService()
        template = await template_service.create_template(template_request)
        return template
    except Exception as e:
        logger.error(f"Failed to create template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create template")


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: str, template_request: TemplateRequest):
    """
    Update an existing template
    """
    try:
        template_service = TemplateService()
        template = await template_service.update_template(template_id, template_request)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update template")


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """
    Delete a template
    """
    try:
        template_service = TemplateService()
        success = await template_service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete template")


@router.get("/{template_id}/usage", response_model=TemplateUsage)
async def get_template_usage(template_id: str):
    """
    Get template usage statistics
    """
    try:
        template_service = TemplateService()
        usage = await template_service.get_template_usage(template_id)
        if not usage:
            raise HTTPException(status_code=404, detail="Template not found")
        return usage
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template usage {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get template usage")


@router.post("/{template_id}/rate")
async def rate_template(template_id: str, rating: int):
    """
    Rate a template (1-5 stars)
    """
    try:
        if not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        template_service = TemplateService()
        success = await template_service.rate_template(template_id, rating)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template rated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to rate template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to rate template")

