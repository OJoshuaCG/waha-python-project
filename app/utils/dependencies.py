"""
Dependency Injection Module.

This module provides FastAPI dependency injection for controllers
and the Waha client.
"""

from typing import Generator

from fastapi import Depends

from app.controllers.file_controller import FileController
from app.controllers.group_controller import GroupController
from app.controllers.message_controller import MessageController
from app.controllers.session_controller import SessionController
from app.utils.waha_client import WahaClient


waha_client: WahaClient = WahaClient()


def get_waha_client() -> Generator[WahaClient, None, None]:
    """
    Dependency to get the Waha client instance.

    Yields:
        WahaClient instance.
    """
    yield waha_client


def get_session_controller(
    waha_client: WahaClient = Depends(get_waha_client),
) -> SessionController:
    """
    Dependency to get the SessionController.

    Args:
        waha_client: WahaClient instance.

    Returns:
        SessionController instance.
    """
    return SessionController(waha_client)


def get_message_controller(
    waha_client: WahaClient = Depends(get_waha_client),
) -> MessageController:
    """
    Dependency to get the MessageController.

    Args:
        waha_client: WahaClient instance.

    Returns:
        MessageController instance.
    """
    return MessageController(waha_client)


def get_file_controller(
    waha_client: WahaClient = Depends(get_waha_client),
) -> FileController:
    """
    Dependency to get the FileController.

    Args:
        waha_client: WahaClient instance.

    Returns:
        FileController instance.
    """
    return FileController(waha_client)


def get_group_controller(
    waha_client: WahaClient = Depends(get_waha_client),
) -> GroupController:
    """
    Dependency to get the GroupController.

    Args:
        waha_client: WahaClient instance.

    Returns:
        GroupController instance.
    """
    return GroupController(waha_client)
