"""
Session Routes Module.

This module defines API endpoints for managing WhatsApp sessions
including connection, QR code authentication, and session lifecycle.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.controllers.session_controller import SessionController
from app.schemas.whatsapp import (
    SessionCreate,
    SessionResponse,
    SessionStatusResponse,
    QRCodeResponse,
    ErrorResponse,
)
from app.utils.dependencies import get_session_controller, get_waha_client
from app.utils.logger import logger
from app.utils.waha_client import WahaClient

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=201,
    summary="Start a new WhatsApp session",
    description="Starts a new WhatsApp session with the specified name and configuration.",
)
async def start_session(
    session_data: SessionCreate,
    controller: SessionController = Depends(get_session_controller),
) -> SessionResponse:
    """
    Start a new WhatsApp session.

    This endpoint initiates a new WhatsApp session with the given name.
    After starting, use the /qr endpoint to get the QR code for authentication.

    Args:
        session_data: Session creation parameters.

    Returns:
        SessionResponse with session details.
    """
    logger.info(f"Starting session: {session_data.name}")
    try:
        return await controller.start_session(session_data)
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{session_name}/stop",
    summary="Stop a WhatsApp session",
    description="Stops a running WhatsApp session.",
)
async def stop_session(
    session_name: str,
    controller: SessionController = Depends(get_session_controller),
) -> dict:
    """
    Stop a running WhatsApp session.

    Args:
        session_name: Name of the session to stop.

    Returns:
        Status message.
    """
    logger.info(f"Stopping session: {session_name}")
    try:
        return await controller.stop_session(session_name)
    except Exception as e:
        logger.error(f"Failed to stop session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{session_name}",
    response_model=SessionStatusResponse,
    summary="Get session status",
    description="Gets the current status of a WhatsApp session.",
)
async def get_session_status(
    session_name: str,
    controller: SessionController = Depends(get_session_controller),
) -> SessionStatusResponse:
    """
    Get the current status of a session.

    Args:
        session_name: Name of the session.

    Returns:
        SessionStatusResponse with detailed status.
    """
    try:
        return await controller.get_session_status(session_name)
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{session_name}/qr",
    response_model=QRCodeResponse,
    summary="Get QR code for authentication",
    description="Returns the QR code pairing string for WhatsApp authentication.",
)
async def get_qr_code(
    session_name: str,
    controller: SessionController = Depends(get_session_controller),
) -> QRCodeResponse:
    """
    Get QR code for WhatsApp authentication.

    Scan this QR code with your WhatsApp app to connect.

    Args:
        session_name: Name of the session.

    Returns:
        QRCodeResponse with pairing code.
    """
    try:
        return await controller.get_qr_code(session_name)
    except Exception as e:
        logger.error(f"Failed to get QR code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{session_name}/qr/image",
    summary="Get QR code as image",
    description="Returns the QR code as a base64-encoded image.",
)
async def get_qr_code_image(
    session_name: str,
    controller: SessionController = Depends(get_session_controller),
) -> dict:
    """
    Get QR code as a base64 image.

    Args:
        session_name: Name of the session.

    Returns:
        Dictionary with base64 image data.
    """
    try:
        return await controller.get_qr_code_image(session_name)
    except Exception as e:
        logger.error(f"Failed to get QR code image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{session_name}",
    summary="Logout and delete a session",
    description="Logs out and deletes a WhatsApp session.",
)
async def logout_session(
    session_name: str,
    controller: SessionController = Depends(get_session_controller),
) -> dict:
    """
    Logout and delete a session.

    Args:
        session_name: Name of the session to logout.

    Returns:
        Status message.
    """
    try:
        return await controller.logout_session(session_name)
    except Exception as e:
        logger.error(f"Failed to logout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{session_name}/connected",
    summary="Check connection status",
    description="Checks if the WhatsApp session is connected.",
)
async def check_connection(
    session_name: str,
    controller: SessionController = Depends(get_session_controller),
) -> dict:
    """
    Check if WhatsApp is connected.

    Args:
        session_name: Name of the session.

    Returns:
        Dictionary with connection status.
    """
    try:
        return await controller.check_connection(session_name)
    except Exception as e:
        logger.error(f"Failed to check connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
