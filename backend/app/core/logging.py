"""
Logging Configuration
Setup structured logging for the application
"""

import logging
import sys
from datetime import datetime
import json
from loguru import logger


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logging():
    """Configure application logging"""
    # Remove default handlers
    logger.remove()
    
    # Add console handler with JSON format
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        serialize=False,
    )
    
    # Add file handler for errors
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="ERROR",
        rotation="10 MB",
        retention="10 days",
    )
    
    # Configure uvicorn logging
    loggers_to_configure = [
        logging.getLogger(name)
        for name in logging.Logger.manager.loggerDict.keys()
    ]
    
    for log in loggers_to_configure:
        log.setLevel(logging.INFO)
    
    # Suppress some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logger.info("Logging configured successfully")
