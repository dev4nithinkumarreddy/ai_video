import os
import logging
from typing import List, Optional
from pathlib import Path
from pydantic import BaseSettings, validator


class ProductionSettings(BaseSettings):
    """Production environment settings"""
    
    # Application
    APP_NAME: str = "AI Video Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALLOWED_ORIGINS: List[str] = ["https://yourdomain.com"]
    CORS_CREDENTIALS: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    # API Keys (should be loaded from secure sources)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN", "")
    
    # Storage
    STORAGE_TYPE: str = "s3"  # Use S3 in production
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # File Upload Limits
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    MAX_FILES_PER_REQUEST: int = 10
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Static Files
    STATIC_FILES_ENABLED: bool = True
    STATIC_FILES_PATH: str = "/app/static"
    STATIC_FILES_URL: str = "/static"
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    @validator("OPENAI_API_KEY")
    def validate_openai_key(cls, v):
        if not v or not v.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key")
        return v
    
    class Config:
        env_file = str(Path(__file__).resolve().parent.parent / ".env.production")
        case_sensitive = True


def get_production_settings() -> ProductionSettings:
    """Get production settings"""
    return ProductionSettings()
