"""
Routes module initialization.

This module contains API route definitions for the WhatsApp management API.
"""

from .session import router as session_router
from .messages import router as messages_router
from .files import router as files_router
from .groups import router as groups_router
from .health import router as health_router

__all__ = [
    "session_router",
    "messages_router",
    "files_router",
    "groups_router",
    "health_router",
]
