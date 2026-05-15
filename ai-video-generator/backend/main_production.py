import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import os

# Import production utilities
from utils.production_config import get_production_settings
from utils.production_logging import setup_production_logging, LoggingMiddleware
from utils.error_monitoring import setup_error_monitoring, monitor_errors
from utils.secrets import setup_production_secrets
from utils.static_files import setup_static_files
from database.database import init_database, close_database

# Import routes
from routes import health, storage, script_generation, audio, images, video_rendering, websocket

# Setup production logging
production_logger = setup_production_logging()
logger = logging.getLogger(__name__)

# Setup error monitoring
error_monitoring, health_checker = setup_error_monitoring()

# Get production settings
settings = get_production_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan for production"""
    # Startup
    logger.info("Starting AI Video Generator API in production mode...")
    
    # Setup secrets
    if not setup_production_secrets():
        logger.error("Failed to setup production secrets")
        raise RuntimeError("Production secrets not configured")
    
    # Initialize database
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        error_monitoring.capture_exception(e)
        raise
    
    # Setup health checks
    health_checker.add_check("database", check_database_health)
    health_checker.add_check("storage", check_storage_health)
    health_checker.add_check("external_apis", check_external_api_health)
    
    logger.info("AI Video Generator API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Video Generator API...")
    await close_database()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Video Generator Production API",
    docs_url=None,  # Disable docs in production
    redoc_url=None,  # Disable redoc in production
    lifespan=lifespan
)

# Add production middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com", "localhost", "127.0.0.1"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting middleware"""
    if settings.RATE_LIMIT_ENABLED:
        # In production, use Redis for distributed rate limiting
        client_ip = request.client.host
        # Add rate limiting logic here
        pass
    
    response = await call_next(request)
    return response


# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers"""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# Request timing middleware
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """Add request timing"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    error_monitoring.capture_exception(exc, {
        "request_url": str(request.url),
        "method": request.method,
        "status_code": exc.status_code
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    error_monitoring.capture_exception(exc, {
        "request_url": str(request.url),
        "method": request.method,
        "exception_type": type(exc).__name__
    })
    
    logger.error(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time()
        }
    )


# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(storage.router, prefix="/api/storage", tags=["storage"])
app.include_router(script_generation.router, prefix="/api", tags=["script-generation"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(video_rendering.router, prefix="/api/video-rendering", tags=["video-rendering"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


# Setup static file serving
if settings.STATIC_FILES_ENABLED:
    setup_static_files(app, settings.STATIC_FILES_PATH)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Comprehensive health check"""
    try:
        results = await health_checker.run_checks()
        overall_status = health_checker.get_overall_status()
        
        return JSONResponse(
            status_code=200 if overall_status == "healthy" else 503,
            content={
                "status": overall_status,
                "timestamp": time.time(),
                "version": settings.APP_VERSION,
                "checks": results
            }
        )
    except Exception as e:
        error_monitoring.capture_exception(e)
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


# Metrics endpoint (for monitoring)
@app.get("/api/metrics")
async def metrics():
    """Basic metrics for monitoring"""
    return {
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "uptime": time.time(),  # Would be calculated from startup time
        "memory_usage": os.getsize(os.getcwd()) if hasattr(os, 'getsize') else 0
    }


# Health check functions
async def check_database_health():
    """Check database health"""
    try:
        # Add actual database health check
        return {"status": "healthy", "connection": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_storage_health():
    """Check storage health"""
    try:
        # Add actual storage health check
        return {"status": "healthy", "storage": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_external_api_health():
    """Check external API health"""
    try:
        # Add actual API health checks
        return {"status": "healthy", "apis": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Video Generator API",
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run with production settings
    uvicorn.run(
        "main_production:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Multiple workers for production
        access_log=False,  # We handle logging ourselves
        log_level="warning"  # Reduce uvicorn logging
    )
