from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging
import asyncio
from datetime import datetime
import psutil
import sys
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    system_info: Dict[str, Any]
    dependencies: Dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns the health status of the API and its dependencies
    """
    try:
        # Get system information
        system_info = {
            "python_version": sys.version,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if sys.platform != 'win32' else psutil.disk_usage('C:').percent,
        }
        
        # Check dependencies
        dependencies = {
            "fastapi": "healthy",
            "uvicorn": "healthy",
        }
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime=psutil.boot_time(),
            system_info=system_info,
            dependencies=dependencies
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check endpoint
    Used by Kubernetes to determine if the pod is ready to serve traffic
    """
    # Add any readiness checks here (database connection, etc.)
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check endpoint
    Used by Kubernetes to determine if the pod is still alive
    """
    return {"status": "alive", "timestamp": datetime.utcnow()}


@router.get("/health/version")
async def version_check():
    """
    Version check endpoint
    Returns the current API version
    """
    return {
        "version": "1.0.0",
        "name": "AI Video Generator API",
        "description": "Backend API for AI-powered video generation"
    }
