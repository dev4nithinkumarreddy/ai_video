from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
import time

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from utils.logging_config import setup_logging
from utils.config import get_settings
from utils.env_validator import validate_environment
from utils.logging_middleware import setup_api_logging_middleware
from routes import health, storage, videos, scripts, templates, script_generation, audio, images, video_rendering, websocket
from database.database import init_database, close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger = logging.getLogger(__name__)
    startup_start = time.time()
    
    logger.info("=" * 80)
    logger.info("Starting AI Video Generator API...")
    logger.info("=" * 80)
    
    # Log configuration
    settings = get_settings()
    logger.info(f"[Startup] Configuration:")
    logger.info(f"  - Host: {settings.HOST}")
    logger.info(f"  - Port: {settings.PORT}")
    logger.info(f"  - Debug Mode: {settings.DEBUG}")
    logger.info(f"  - Log Level: {settings.LOG_LEVEL}")
    logger.info(f"  - Allowed Origins: {len(settings.ALLOWED_ORIGINS)} origins")
    
    # Validate environment variables
    try:
        logger.info("[Startup] Validating environment variables...")
        validate_start = time.time()
        validate_environment()
        validate_duration = time.time() - validate_start
        logger.info(f"[Startup] Environment validation passed ({validate_duration:.2f}s)")
    except EnvironmentError as e:
        logger.error(f"[Startup] Environment validation failed: {str(e)}")
        raise
    
    # Initialize database
    try:
        logger.info("[Startup] Initializing database...")
        db_start = time.time()
        await init_database()
        db_duration = time.time() - db_start
        logger.info(f"[Startup] Database initialized successfully ({db_duration:.2f}s)")
    except Exception as e:
        logger.error(f"[Startup] Failed to initialize database: {str(e)}")
        raise
    
    startup_duration = time.time() - startup_start
    logger.info(f"[Startup] Startup completed in {startup_duration:.2f}s")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("Shutting down AI Video Generator API...")
    logger.info("=" * 80)
    try:
        logger.info("[Shutdown] Closing database connections...")
        await close_database()
        logger.info("[Shutdown] Database connections closed")
    except Exception as e:
        logger.error(f"[Shutdown] Error closing database: {str(e)}")
    logger.info("[Shutdown] Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="AI Video Generator API",
    description="Backend API for AI-powered video generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup API logging middleware
setup_api_logging_middleware(app, debug_mode=settings.DEBUG)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])

app.include_router(storage.router, prefix="/api/storage", tags=["storage"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(scripts.router, prefix="/api/scripts", tags=["scripts"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(script_generation.router, prefix="/api", tags=["script-generation"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(video_rendering.router, prefix="/api/video-rendering", tags=["video-rendering"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Video Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_excludes=["*.db", "*.sqlite", "*.log", "logs/*", "__pycache__/*"],
        log_level="info"
    )
