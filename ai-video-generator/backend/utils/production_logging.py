import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", 
                          "pathname", "filename", "module", "exc_info", 
                          "exc_text", "stack_info", "lineno", "funcName", 
                          "created", "msecs", "relativeCreated", "thread", 
                          "threadName", "processName", "process", "getMessage"]:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class ProductionLogger:
    """Production logging configuration"""
    
    def __init__(self, app_name: str = "ai_video_generator"):
        self.app_name = app_name
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up loggers
        self.setup_logging()
    
    def setup_logging(self):
        """Setup production logging"""
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = JSONFormatter()
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handlers
        self.setup_file_handlers(root_logger)
        
        # Application-specific loggers
        self.setup_app_loggers()
    
    def setup_file_handlers(self, logger: logging.Logger):
        """Setup file handlers for different log levels"""
        
        # General log file
        general_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(JSONFormatter())
        logger.addHandler(general_handler)
        
        # Error log file
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        logger.addHandler(error_handler)
        
        # Security log file
        security_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "security.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        security_handler.setLevel(logging.INFO)
        security_handler.setFormatter(JSONFormatter())
        
        # Create security logger
        security_logger = logging.getLogger("security")
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
    
    def setup_app_loggers(self):
        """Setup application-specific loggers"""
        
        # API logger
        api_logger = logging.getLogger("api")
        api_logger.setLevel(logging.INFO)
        
        # Database logger
        db_logger = logging.getLogger("database")
        db_logger.setLevel(logging.INFO)
        
        # Storage logger
        storage_logger = logging.getLogger("storage")
        storage_logger.setLevel(logging.INFO)
        
        # External services logger
        external_logger = logging.getLogger("external")
        external_logger.setLevel(logging.INFO)
    
    @staticmethod
    def log_api_request(request_id: str, method: str, path: str, 
                       user_id: str = None, ip_address: str = None):
        """Log API request"""
        logger = logging.getLogger("api")
        logger.info(
            f"API request: {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "user_id": user_id,
                "ip_address": ip_address,
                "type": "api_request"
            }
        )
    
    @staticmethod
    def log_api_response(request_id: str, status_code: int, 
                         response_time: float, error: str = None):
        """Log API response"""
        logger = logging.getLogger("api")
        log_data = {
            "request_id": request_id,
            "status_code": status_code,
            "response_time": response_time,
            "type": "api_response"
        }
        
        if error:
            log_data["error"] = error
            logger.error(f"API response error: {error}", extra=log_data)
        else:
            logger.info(f"API response: {status_code}", extra=log_data)
    
    @staticmethod
    def log_security_event(event_type: str, user_id: str = None, 
                          ip_address: str = None, details: Dict[str, Any] = None):
        """Log security event"""
        logger = logging.getLogger("security")
        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "security_event"
        }
        
        if details:
            log_data.update(details)
        
        logger.info(f"Security event: {event_type}", extra=log_data)
    
    @staticmethod
    def log_database_operation(operation: str, table: str, 
                              duration: float, error: str = None):
        """Log database operation"""
        logger = logging.getLogger("database")
        log_data = {
            "operation": operation,
            "table": table,
            "duration": duration,
            "type": "database_operation"
        }
        
        if error:
            log_data["error"] = error
            logger.error(f"Database error: {error}", extra=log_data)
        else:
            logger.info(f"Database operation: {operation} on {table}", extra=log_data)
    
    @staticmethod
    def log_external_service_call(service: str, endpoint: str, 
                                 method: str, status_code: int, 
                                 duration: float, error: str = None):
        """Log external service call"""
        logger = logging.getLogger("external")
        log_data = {
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration": duration,
            "type": "external_service"
        }
        
        if error:
            log_data["error"] = error
            logger.error(f"External service error: {service} {error}", extra=log_data)
        else:
            logger.info(f"External service call: {service} {endpoint}", extra=log_data)


def setup_production_logging(app_name: str = "ai_video_generator") -> ProductionLogger:
    """Setup production logging"""
    return ProductionLogger(app_name)


# Logging middleware for FastAPI
class LoggingMiddleware:
    """Middleware for logging API requests and responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            import time
            import uuid
            
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            # Get request details
            method = scope["method"]
            path = scope["path"]
            client = scope.get("client", ["", ""])[0]
            
            # Log request
            ProductionLogger.log_api_request(
                request_id=request_id,
                method=method,
                path=path,
                ip_address=client
            )
            
            # Process request
            await self.app(scope, receive, send)
            
            # Log response (simplified - in real implementation, 
            # you'd need to capture response status and time)
            end_time = time.time()
            duration = end_time - start_time
            
            ProductionLogger.log_api_response(
                request_id=request_id,
                status_code=200,  # This would be captured from response
                response_time=duration
            )
        else:
            await self.app(scope, receive, send)
