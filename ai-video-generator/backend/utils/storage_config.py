import os
from typing import Optional
from pathlib import Path
from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.parent / ".env"


class StorageSettings(BaseSettings):
    """Storage configuration settings"""
    
    # Storage type: 'local' or 's3'
    STORAGE_TYPE: str = "local"
    
    # Local storage settings
    STORAGE_PATH: str = "generated"
    PUBLIC_URL_BASE: str = "http://localhost:8000/generated"
    
    # AWS S3 settings
    AWS_S3_BUCKET: str = "ai-video-storage"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_URL_EXPIRES_IN: int = 3600  # URL expiration in seconds
    
    # File cleanup settings
    AUTO_CLEANUP_ENABLED: bool = True
    CLEANUP_INTERVAL_HOURS: int = 24
    MAX_FILE_AGE_DAYS: int = 30
    
    # File size limits (in bytes)
    MAX_VIDEO_SIZE: int = 500 * 1024 * 1024  # 500MB
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024     # 10MB
    MAX_AUDIO_SIZE: int = 50 * 1024 * 1024    # 50MB
    MAX_SCRIPT_SIZE: int = 1 * 1024 * 1024    # 1MB
    
    # Allowed file types
    ALLOWED_VIDEO_TYPES: list = [".mp4", ".mov", ".avi", ".webm"]
    ALLOWED_IMAGE_TYPES: list = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
    ALLOWED_AUDIO_TYPES: list = [".mp3", ".wav", ".m4a", ".ogg"]
    ALLOWED_SCRIPT_TYPES: list = [".json", ".txt"]
    
    # Storage quotas (in bytes)
    USER_STORAGE_QUOTA: int = 5 * 1024 * 1024 * 1024  # 5GB per user
    PROJECT_STORAGE_QUOTA: int = 1 * 1024 * 1024 * 1024  # 1GB per project
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True


def get_storage_settings() -> StorageSettings:
    """Get storage settings"""
    return StorageSettings()
