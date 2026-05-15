"""
API Request Logging Middleware

Logs all incoming API requests with timing, status codes, and error details.
Does not expose sensitive credentials or request bodies in production.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class APILoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests and responses"""
    
    def __init__(self, app: ASGIApp, debug_mode: bool = False):
        super().__init__(app)
        self.debug_mode = debug_mode
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details"""
        start_time = time.time()
        
        # Extract request details
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(f"[API Request] {method} {path} from {client_host}")
        
        if self.debug_mode:
            logger.debug(f"[API Request Details] URL: {url}")
            logger.debug(f"[API Request Details] Headers: {self._sanitize_headers(dict(request.headers))}")
        
        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log response
            status_code = response.status_code
            if status_code >= 500:
                logger.error(f"[API Response] {method} {path} - {status_code} ({duration:.3f}s) - Server Error")
            elif status_code >= 400:
                logger.warning(f"[API Response] {method} {path} - {status_code} ({duration:.3f}s) - Client Error")
            elif status_code >= 300:
                logger.info(f"[API Response] {method} {path} - {status_code} ({duration:.3f}s) - Redirect")
            else:
                logger.info(f"[API Response] {method} {path} - {status_code} ({duration:.3f}s) - Success")
            
            # Add custom header with duration
            response.headers["X-Process-Time"] = f"{duration:.3f}"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[API Error] {method} {path} - Exception after {duration:.3f}s: {str(e)}")
            raise
    
    def _sanitize_headers(self, headers: dict) -> dict:
        """Remove sensitive headers from logs"""
        sensitive_keys = ['authorization', 'cookie', 'x-api-key', 'token']
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = "***"
            else:
                sanitized[key] = value
        return sanitized


def setup_api_logging_middleware(app, debug_mode: bool = False):
    """Add API logging middleware to FastAPI app"""
    app.add_middleware(APILoggingMiddleware, debug_mode=debug_mode)
