"""
Configuration management module.

This module handles all application configuration using environment variables
and Pydantic settings for type validation and documentation.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        WAHA_URL: Base URL of the Waha server instance.
        WAHA_API_KEY: Authentication key for Waha API (if required).
        APP_HOST: Host address for FastAPI server.
        APP_PORT: Port number for FastAPI server.
        APP_DEBUG: Enable debug mode for development.
        UPLOAD_DIR: Directory for storing uploaded files.
        MAX_UPLOAD_SIZE: Maximum file upload size in bytes (default 50MB).
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    WAHA_URL: str = Field(
        default="http://localhost:3000",
        description="Base URL of the Waha server instance",
    )
    WAHA_API_KEY: Optional[str] = Field(
        default=None,
        description="Authentication key for Waha API",
    )
    APP_HOST: str = Field(
        default="0.0.0.0",
        description="Host address for FastAPI server",
    )
    APP_PORT: int = Field(
        default=8000,
        description="Port number for FastAPI server",
        ge=1,
        le=65535,
    )
    APP_DEBUG: bool = Field(
        default=False,
        description="Enable debug mode for development",
    )
    UPLOAD_DIR: Path = Field(
        default=Path("uploads"),
        description="Directory for storing uploaded files",
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=50 * 1024 * 1024,
        description="Maximum file upload size in bytes",
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )


settings = Settings()
"""
Global settings instance for application-wide configuration access.
"""
