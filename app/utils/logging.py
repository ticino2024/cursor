"""Logging configuration and utilities."""

import logging
import sys
from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create formatter
    if settings.is_production:
        # JSON formatter for production
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"}
        )
    else:
        # Simple formatter for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class SecurityLogger:
    """Logger for security-related events."""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
    
    def log_authentication_attempt(self, user_id: str, success: bool, ip_address: str) -> None:
        """Log authentication attempts."""
        event = {
            "event_type": "authentication_attempt",
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address
        }
        
        if success:
            self.logger.info(f"Successful authentication: {event}")
        else:
            self.logger.warning(f"Failed authentication: {event}")
    
    def log_authorization_failure(self, user_id: str, resource: str, action: str) -> None:
        """Log authorization failures."""
        event = {
            "event_type": "authorization_failure",
            "user_id": user_id,
            "resource": resource,
            "action": action
        }
        self.logger.warning(f"Authorization failure: {event}")
    
    def log_suspicious_activity(self, user_id: str, activity: str, details: dict) -> None:
        """Log suspicious activities."""
        event = {
            "event_type": "suspicious_activity",
            "user_id": user_id,
            "activity": activity,
            "details": details
        }
        self.logger.error(f"Suspicious activity: {event}")


# Global security logger instance
security_logger = SecurityLogger()
