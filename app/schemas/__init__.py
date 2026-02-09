"""
Schemas module initialization.

This module contains Pydantic models for API request/response schemas.
"""

from .whatsapp import (
    SessionCreate,
    SessionResponse,
    SessionStatusResponse,
    QRCodeResponse,
    MessageSend,
    MessageResponse,
    FileSend,
    FileResponse,
    ChatResponse,
    ChatMessagesRequest,
    GroupCreate,
    GroupResponse,
    WebhookConfig,
    HealthResponse,
    ErrorResponse,
)

__all__ = [
    "SessionCreate",
    "SessionResponse",
    "SessionStatusResponse",
    "QRCodeResponse",
    "MessageSend",
    "MessageResponse",
    "FileSend",
    "FileResponse",
    "ChatResponse",
    "ChatMessagesRequest",
    "GroupCreate",
    "GroupResponse",
    "WebhookConfig",
    "HealthResponse",
    "ErrorResponse",
]
