"""
Logging Configuration
Centralized logging setup for the application
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure application logging with both file and console handlers
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    log_filename = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Create formatters
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
