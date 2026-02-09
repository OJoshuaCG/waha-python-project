"""
Logging configuration module.

This module provides centralized logging configuration using Loguru
for consistent and beautiful logging throughout the application.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.config import settings


def setup_logger(
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    level: Optional[str] = None,
) -> None:
    """
    Configure application logging with Loguru.

    This function sets up the logger with console and optional file output.
    It removes the default handler and adds custom handlers with proper
    formatting.

    Args:
        log_file: Optional path to log file. If not provided, only console logging.
        rotation: Log file rotation size (default: "10 MB").
        retention: How long to keep log files (default: "1 week").
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    log_level = level or settings.LOG_LEVEL

    logger.remove()

    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=console_format,
        level=log_level,
        colorize=True,
    )

    if log_file or settings.APP_DEBUG:
        log_path = Path(log_file) if log_file else Path("logs/app.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
        )

        logger.add(
            str(log_path),
            format=file_format,
            level=log_level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
            serialize=False,
        )

    logger.info(f"Logger initialized with level: {log_level}")


setup_logger()
