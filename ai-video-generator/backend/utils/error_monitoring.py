import logging
import traceback
import sys
from typing import Optional, Dict, Any
from functools import wraps
import asyncio
from datetime import datetime

# Try to import Sentry
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ErrorMonitoring:
    """Error monitoring and reporting"""
    
    def __init__(self, dsn: Optional[str] = None, environment: str = "production"):
        self.dsn = dsn
        self.environment = environment
        self.enabled = bool(dsn and SENTRY_AVAILABLE)
        
        if self.enabled:
            self.setup_sentry()
    
    def setup_sentry(self):
        """Setup Sentry error monitoring"""
        try:
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                integrations=[
                    FastApiIntegration(auto_enabling_integrations=False),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                ],
                traces_sample_rate=0.1,  # Sample 10% of transactions
                send_default_pii=False,
                before_send=self.before_send,
            )
            logger.info("Sentry error monitoring enabled")
        except Exception as e:
            logger.error(f"Failed to setup Sentry: {str(e)}")
            self.enabled = False
    
    def before_send(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Filter and modify events before sending"""
        # Filter out sensitive data
        if "request" in event:
            request = event["request"]
            if "headers" in request:
                # Remove sensitive headers
                sensitive_headers = ["authorization", "cookie", "x-api-key"]
                request["headers"] = {
                    k: v for k, v in request["headers"].items() 
                    if k.lower() not in sensitive_headers
                }
        
        return event
    
    def capture_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Capture exception"""
        if self.enabled:
            sentry_sdk.capture_exception(exception)
        
        # Always log locally
        logger.error(
            f"Exception captured: {str(exception)}",
            extra={
                "exception_type": type(exception).__name__,
                "context": context,
                "traceback": traceback.format_exc()
            }
        )
    
    def capture_message(self, message: str, level: str = "info"):
        """Capture message"""
        if self.enabled:
            sentry_sdk.capture_message(message, level=level)
        
        # Always log locally
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, message)
    
    def set_user_context(self, user_data: Dict[str, Any]):
        """Set user context"""
        if self.enabled:
            sentry_sdk.set_user(user_data)
    
    def set_tag(self, key: str, value: str):
        """Set tag"""
        if self.enabled:
            sentry_sdk.set_tag(key, value)
    
    def add_breadcrumb(self, message: str, category: str = "custom", 
                      level: str = "info", data: Optional[Dict[str, Any]] = None):
        """Add breadcrumb"""
        if self.enabled:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data
            )


def monitor_errors(dsn: Optional[str] = None, environment: str = "production"):
    """Decorator to monitor function errors"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                monitoring = ErrorMonitoring(dsn, environment)
                monitoring.capture_exception(e, {
                    "function": func.__name__,
                    "args": str(args)[:100],  # Limit size
                    "kwargs": str(kwargs)[:100]
                })
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                monitoring = ErrorMonitoring(dsn, environment)
                monitoring.capture_exception(e, {
                    "function": func.__name__,
                    "args": str(args)[:100],
                    "kwargs": str(kwargs)[:100]
                })
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class HealthChecker:
    """Health check monitoring"""
    
    def __init__(self):
        self.checks = {}
        self.last_results = {}
    
    def add_check(self, name: str, check_func):
        """Add health check"""
        self.checks[name] = check_func
    
    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "details": result if isinstance(result, dict) else {}
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
        
        self.last_results = results
        return results
    
    def get_overall_status(self) -> str:
        """Get overall health status"""
        if not self.last_results:
            return "unknown"
        
        statuses = [check["status"] for check in self.last_results.values()]
        
        if all(status == "healthy" for status in statuses):
            return "healthy"
        elif any(status == "error" for status in statuses):
            return "error"
        else:
            return "degraded"


# Global error monitoring instance
_error_monitoring: Optional[ErrorMonitoring] = None
_health_checker: Optional[HealthChecker] = None


def get_error_monitoring() -> ErrorMonitoring:
    """Get global error monitoring instance"""
    global _error_monitoring
    if _error_monitoring is None:
        from utils.production_config import get_production_settings
        settings = get_production_settings()
        _error_monitoring = ErrorMonitoring(
            dsn=settings.SENTRY_DSN,
            environment="production"
        )
    return _error_monitoring


def get_health_checker() -> HealthChecker:
    """Get global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def setup_error_monitoring():
    """Setup error monitoring"""
    monitoring = get_error_monitoring()
    checker = get_health_checker()
    
    # Add basic health checks
    checker.add_check("database", lambda: True)  # Would check DB connection
    checker.add_check("redis", lambda: True)     # Would check Redis connection
    checker.add_check("storage", lambda: True)   # Would check storage
    
    return monitoring, checker
