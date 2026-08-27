from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3002",  # Current Vite port
        "http://127.0.0.1:3002",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
        "http://localhost:8000",  # Frontend development port
        "http://127.0.0.1:8000",
        "http://localhost:8000/api",  # API base URL
        "http://127.0.0.1:8000/api"
    ]
    
    # Database settings (optional)
    DATABASE_URL: Optional[str] = None
    
    # API settings
    API_V1_STR: str = "/api"
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = 30
    
    # File upload settings
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "uploads"
    
    # AI/ML settings
    GROQ_API_KEY: Optional[str] = None
    GROQ_BASE_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None  # Legacy, replaced by Groq
    HUGGINGFACE_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    REPLICATE_API_TOKEN: Optional[str] = None
    INFERENCE_MODE: str = "hosted"  # 'hosted' or 'local'
    IMAGE_PROVIDER: str = "pollinations" # 'hosted', 'local', 'pollinations'
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Video processing settings
    MAX_VIDEO_DURATION: int = 600  # 10 minutes
    VIDEO_QUALITY: str = "720p"
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def create_upload_dir() -> Path:
    """Create upload directory if it doesn't exist"""
    settings = get_settings()
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(exist_ok=True)
    return upload_path
