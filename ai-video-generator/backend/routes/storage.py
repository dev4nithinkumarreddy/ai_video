import logging
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
import os
import mimetypes

from services.storage_service import get_storage_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload/video")
async def upload_video(
    file: UploadFile = File(...),
    project_id: str = Form(...)
):
    """Upload a video file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.mp4', '.mov', '.avi', '.webm')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid video file type"
            )
        
        # Read file content
        content = await file.read()
        
        # Save using storage service
        storage_service = get_storage_service()
        file_path = await storage_service.save_video(content, project_id, file.filename)
        
        # Get file URL
        file_url = await storage_service.get_file_url(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_url": file_url,
            "file_size": len(content),
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    scene_id: str = Form(...)
):
    """Upload an image file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file type"
            )
        
        # Read file content
        content = await file.read()
        
        # Save using storage service
        storage_service = get_storage_service()
        file_path = await storage_service.save_image(content, project_id, scene_id, file.filename)
        
        # Get file URL
        file_url = await storage_service.get_file_url(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_url": file_url,
            "file_size": len(content),
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/upload/audio")
async def upload_audio(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    scene_id: str = Form(...)
):
    """Upload an audio file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio file type"
            )
        
        # Read file content
        content = await file.read()
        
        # Save using storage service
        storage_service = get_storage_service()
        file_path = await storage_service.save_audio(content, project_id, scene_id, file.filename)
        
        # Get file URL
        file_url = await storage_service.get_file_url(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_url": file_url,
            "file_size": len(content),
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload audio: {str(e)}"
        )


@router.get("/file/{file_path:path}")
async def get_file(file_path: str):
    """Get file content"""
    try:
        storage_service = get_storage_service()
        
        # Check if file exists
        if not await storage_service.file_exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Get file content
        content = await storage_service.get_file(file_path)
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        # Return file
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=mime_type,
            headers={
                "Content-Disposition": f"inline; filename={os.path.basename(file_path)}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file {file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file: {str(e)}"
        )


@router.delete("/file/{file_path:path}")
async def delete_file(
    file_path: str
):
    """Delete a file"""
    try:
        storage_service = get_storage_service()
        
        # Check if file exists
        if not await storage_service.file_exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete file
        success = await storage_service.delete_file(file_path)
        
        if success:
            return {"success": True, "message": "File deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/file/{file_path:path}/info")
async def get_file_info(file_path: str):
    """Get file information"""
    try:
        storage_service = get_storage_service()
        file_info = await storage_service.get_file_info(file_path)
        
        if not file_info.get('exists'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info {file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}"
        )


@router.get("/project/{project_id}/files")
async def get_project_files(
    project_id: str
):
    """Get all files for a project"""
    try:
        storage_service = get_storage_service()
        files = await storage_service.list_project_files(project_id)
        
        # Add file URLs and sizes
        result = {}
        for file_type, file_list in files.items():
            result[file_type] = []
            for file_path in file_list:
                file_info = await storage_service.get_file_info(file_path)
                result[file_type].append(file_info)
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing project files {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list project files: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_old_files(
    max_age_days: int = 30
):
    """Clean up old files"""
    try:
        storage_service = get_storage_service()
        deleted_counts = await storage_service.cleanup_old_files(max_age_days)
        
        total_deleted = sum(deleted_counts.values())
        
        return {
            "success": True,
            "deleted_counts": deleted_counts,
            "total_deleted": total_deleted,
            "max_age_days": max_age_days
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup files: {str(e)}"
        )


@router.get("/stats")
async def get_storage_stats():
    """Get storage statistics"""
    try:
        storage_service = get_storage_service()
        stats = await storage_service.get_storage_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage stats: {str(e)}"
        )


@router.get("/url/{file_path:path}")
async def get_file_url(file_path: str):
    """Get public URL for a file"""
    try:
        storage_service = get_storage_service()
        
        # Check if file exists
        if not await storage_service.file_exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Get file URL
        file_url = await storage_service.get_file_url(file_path)
        
        return {"file_url": file_url}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file URL {file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file URL: {str(e)}"
        )
