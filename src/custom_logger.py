"""
Custom logging module for tweakio-sdk.
Supports separate loggers for application and browser events.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict

try:
    from colorlog import ColoredFormatter
except ImportError:
    ColoredFormatter = None

from src.directory import DirectoryManager

class TweakioLogger:
    """
    Centralized logger management for Tweakio SDK.
    Handles both general application logs and specialized browser logs.
    """
    _instances: Dict[str, logging.Logger] = {}
    
    # Default configurations
    MAX_BYTES = 20 * 1024 * 1024  # 20 MB
    BACKUP_COUNT = 3
    LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    CONSOLE_FORMAT = "%(log_color)s%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    @classmethod
    def get_logger(
        cls, 
        name: str = "tweakio", 
        log_type: str = "app",
        level: int = logging.INFO
    ) -> logging.Logger:
        """
        Get or create a logger instance.
        
        Args:
            name: The name of the logger.
            log_type: 'app' for general logs, 'browser' for browser-specific logs.
            level: Logging level (default: logging.INFO).
            
        Returns:
            A configured logging.Logger instance.
        """
        logger_key = f"{log_type}:{name}"
        if logger_key in cls._instances:
            return cls._instances[logger_key]

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False  # Avoid duplicate logs in parent loggers

        # Determine file path based on log type
        dm = DirectoryManager()
        if log_type == "browser":
            log_file = dm.get_browser_log_file()
        else:
            log_file = dm.get_error_trace_file()

        # Add handlers if they don't exist
        if not logger.handlers:
            # Console Handler
            cls._add_console_handler(logger)
            # File Handler
            cls._add_file_handler(logger, log_file)

        cls._instances[logger_key] = logger
        return logger

    @classmethod
    def _add_console_handler(cls, logger: logging.Logger):
        """Adds a console handler to the logger."""
        if ColoredFormatter:
            console_formatter = ColoredFormatter(
                cls.CONSOLE_FORMAT,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red'
                }
            )
        else:
            console_formatter = logging.Formatter(cls.LOG_FORMAT)
            
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    @classmethod
    def _add_file_handler(cls, logger: logging.Logger, log_file: Path):
        """Adds a rotating file handler to the logger."""
        os.makedirs(log_file.parent, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=cls.MAX_BYTES,
            backupCount=cls.BACKUP_COUNT
        )
        file_formatter = logging.Formatter(cls.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

# For backward compatibility if needed, but the plan is to refactor imports
logger = TweakioLogger.get_logger("tweakio", "app")
browser_logger = TweakioLogger.get_logger("tweakio.browser", "browser")
