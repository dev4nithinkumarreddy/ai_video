import logging
import os
import shutil
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import mimetypes

from utils.config import get_settings

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def save_file(self, file_data: bytes, file_path: str) -> str:
        """Save file and return the file path"""
        pass
    
    @abstractmethod
    async def get_file(self, file_path: str) -> bytes:
        """Get file content"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        pass
    
    @abstractmethod
    async def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        pass
    
    @abstractmethod
    async def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in directory"""
        pass


class LocalStorageBackend(StorageBackend):
    """Local file system storage backend"""
    
    def __init__(self, base_path: str, public_url_base: str):
        self.base_path = Path(base_path)
        self.public_url_base = public_url_base.rstrip('/')
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure storage directories exist"""
        directories = [
            self.base_path / "videos",
            self.base_path / "images", 
            self.base_path / "audio",
            self.base_path / "temp",
            self.base_path / "projects"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Storage directories created in {self.base_path}")
    
    def _get_full_path(self, file_path: str) -> Path:
        """Get full file system path"""
        return self.base_path / file_path
    
    def _get_relative_path(self, file_path: str) -> str:
        """Get relative path from base"""
        return str(Path(file_path).relative_to(self.base_path))
    
    async def save_file(self, file_data: bytes, file_path: str) -> str:
        """Save file to local storage"""
        try:
            full_path = self._get_full_path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {str(e)}")
            raise
    
    async def get_file(self, file_path: str) -> bytes:
        """Get file content from local storage"""
        try:
            full_path = self._get_full_path(file_path)
            
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(full_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error getting file {file_path}: {str(e)}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            full_path = self._get_full_path(file_path)
            
            if not full_path.exists():
                return False
            
            full_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local storage"""
        try:
            full_path = self._get_full_path(file_path)
            return full_path.exists()
        except Exception as e:
            logger.error(f"Error checking file existence {file_path}: {str(e)}")
            return False
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        return f"{self.public_url_base}/{file_path}"
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            full_path = self._get_full_path(file_path)
            return full_path.stat().st_size if full_path.exists() else 0
        except Exception as e:
            logger.error(f"Error getting file size {file_path}: {str(e)}")
            return 0
    
    async def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in directory"""
        try:
            full_path = self._get_full_path(directory)
            if not full_path.exists():
                return []
            
            files = []
            for file_path in full_path.glob(pattern):
                if file_path.is_file():
                    relative_path = self._get_relative_path(str(file_path))
                    files.append(relative_path)
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {str(e)}")
            return []


class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend"""
    
    def __init__(self, bucket_name: str, region: str, access_key: str, secret_key: str):
        self.bucket_name = bucket_name
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        
        # Import boto3 only when needed
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
        except ImportError:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
    
    async def save_file(self, file_data: bytes, file_path: str) -> str:
        """Save file to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_data
            )
            logger.info(f"File saved to S3: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving file to S3 {file_path}: {str(e)}")
            raise
    
    async def get_file(self, file_path: str) -> bytes:
        """Get file content from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error getting file from S3 {file_path}: {str(e)}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            logger.info(f"File deleted from S3: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from S3 {file_path}: {str(e)}")
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except:
            return False
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for S3 file"""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_path}"
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size from S3"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return response['ContentLength']
        except Exception as e:
            logger.error(f"Error getting file size from S3 {file_path}: {str(e)}")
            return 0
    
    async def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in S3 directory"""
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            files = []
            
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=directory):
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if key.startswith(directory) and not key.endswith('/'):
                        files.append(key)
            
            return files
        except Exception as e:
            logger.error(f"Error listing files in S3 {directory}: {str(e)}")
            return []


class StorageService:
    """Main storage service with multiple backend support"""
    
    def __init__(self):
        self.settings = get_settings()
        self.backend = self._initialize_backend()
        self.cleanup_task = None
    
    def _initialize_backend(self) -> StorageBackend:
        """Initialize storage backend based on configuration"""
        storage_type = getattr(self.settings, 'STORAGE_TYPE', 'local').lower()
        
        if storage_type == 's3':
            return S3StorageBackend(
                bucket_name=getattr(self.settings, 'AWS_S3_BUCKET', 'ai-video-storage'),
                region=getattr(self.settings, 'AWS_REGION', 'us-east-1'),
                access_key=getattr(self.settings, 'AWS_ACCESS_KEY_ID', ''),
                secret_key=getattr(self.settings, 'AWS_SECRET_ACCESS_KEY', '')
            )
        else:
            # Default to local storage
            base_path = getattr(self.settings, 'STORAGE_PATH', 'generated')
            public_url = getattr(self.settings, 'PUBLIC_URL_BASE', 'http://localhost:8000/generated')
            return LocalStorageBackend(base_path, public_url)
    
    async def save_video(self, video_data: bytes, project_id: str, filename: Optional[str] = None) -> str:
        """Save video file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"video_{timestamp}.mp4"
        
        file_path = f"videos/{project_id}/{filename}"
        return await self.backend.save_file(video_data, file_path)
    
    async def save_image(self, image_data: bytes, project_id: str, scene_id: str, filename: Optional[str] = None) -> str:
        """Save image file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"scene_{scene_id}_{timestamp}.png"
        
        file_path = f"images/{project_id}/{scene_id}/{filename}"
        return await self.backend.save_file(image_data, file_path)
    
    async def save_audio(self, audio_data: bytes, project_id: str, scene_id: str, filename: Optional[str] = None) -> str:
        """Save audio file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"scene_{scene_id}_{timestamp}.mp3"
        
        file_path = f"audio/{project_id}/{scene_id}/{filename}"
        return await self.backend.save_file(audio_data, file_path)
    
    async def save_script(self, script_data: Union[str, bytes, dict], project_id: str, filename: Optional[str] = None) -> str:
        """Save script file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"script_{timestamp}.json"
        
        if isinstance(script_data, dict):
            import json
            script_data = json.dumps(script_data, indent=2).encode('utf-8')
        elif isinstance(script_data, str):
            script_data = script_data.encode('utf-8')
        
        file_path = f"scripts/{project_id}/{filename}"
        return await self.backend.save_file(script_data, file_path)
    
    async def get_file(self, file_path: str) -> bytes:
        """Get file content"""
        return await self.backend.get_file(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        return await self.backend.delete_file(file_path)
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return await self.backend.file_exists(file_path)
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        return await self.backend.get_file_url(file_path)
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return await self.backend.get_file_size(file_path)
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            size = await self.get_file_size(file_path)
            exists = await self.file_exists(file_path)
            url = await self.get_file_url(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'file_path': file_path,
                'size': size,
                'exists': exists,
                'url': url,
                'mime_type': mime_type,
                'extension': Path(file_path).suffix,
                'created_at': datetime.fromtimestamp(os.path.getctime(file_path)) if exists else None
            }
        except Exception as e:
            logger.error(f"Error getting file info {file_path}: {str(e)}")
            return {'file_path': file_path, 'error': str(e)}
    
    async def list_project_files(self, project_id: str) -> Dict[str, List[str]]:
        """List all files for a project"""
        try:
            files = {
                'videos': await self.backend.list_files(f"videos/{project_id}", "*.mp4"),
                'images': await self.backend.list_files(f"images/{project_id}", "*.png"),
                'audio': await self.backend.list_files(f"audio/{project_id}", "*.mp3"),
                'scripts': await self.backend.list_files(f"scripts/{project_id}", "*.json")
            }
            return files
        except Exception as e:
            logger.error(f"Error listing project files {project_id}: {str(e)}")
            return {'videos': [], 'images': [], 'audio': [], 'scripts': []}
    
    async def cleanup_old_files(self, max_age_days: int = 30) -> Dict[str, int]:
        """Clean up old files"""
        deleted_counts = {'videos': 0, 'images': 0, 'audio': 0, 'scripts': 0}
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        try:
            # Get all files
            all_files = []
            for file_type in ['videos', 'images', 'audio', 'scripts']:
                files = await self.backend.list_files(file_type)
                all_files.extend([(file_type, file) for file in files])
            
            # Check and delete old files
            for file_type, file_path in all_files:
                try:
                    full_path = self.backend._get_full_path(file_path) if hasattr(self.backend, '_get_full_path') else None
                    
                    if full_path and full_path.exists():
                        file_mtime = full_path.stat().st_mtime
                        if file_mtime < cutoff_time:
                            if await self.delete_file(file_path):
                                deleted_counts[file_type] += 1
                except Exception as e:
                    logger.error(f"Error checking file {file_path}: {str(e)}")
            
            total_deleted = sum(deleted_counts.values())
            logger.info(f"Cleanup completed. Deleted {total_deleted} files older than {max_age_days} days")
            
            return deleted_counts
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return deleted_counts
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'by_type': {
                    'videos': {'count': 0, 'size': 0},
                    'images': {'count': 0, 'size': 0},
                    'audio': {'count': 0, 'size': 0},
                    'scripts': {'count': 0, 'size': 0}
                }
            }
            
            # Count and size files by type
            for file_type in ['videos', 'images', 'audio', 'scripts']:
                files = await self.backend.list_files(file_type)
                stats['by_type'][file_type]['count'] = len(files)
                
                for file_path in files:
                    size = await self.get_file_size(file_path)
                    stats['by_type'][file_type]['size'] += size
                    stats['total_size'] += size
                
                stats['total_files'] += len(files)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {'error': str(e)}


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
