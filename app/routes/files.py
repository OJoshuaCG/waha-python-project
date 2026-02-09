"""
File Routes Module.

This module defines API endpoints for sending and receiving files through WhatsApp.
"""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from app.controllers.file_controller import FileController
from app.schemas.whatsapp import (
    FileResponse,
    ErrorResponse,
)
from app.utils.dependencies import get_file_controller
from app.utils.logger import logger

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)


class FileSendRequest(BaseModel):
    """
    Request model for sending files.
    """

    chat_id: str = Query(..., description="WhatsApp ID (phone number or group ID)")
    caption: Optional[str] = Query(None, description="Optional file caption")
    filename: Optional[str] = Query(None, description="Custom filename")


@router.post(
    "/send/{session_name}/path",
    response_model=FileResponse,
    summary="Send file from path",
    description="Sends a file to a WhatsApp chat from a local file path.",
)
async def send_file_from_path(
    session_name: str,
    file_path: str = Query(..., description="Path to the local file"),
    chat_id: str = Query(..., description="WhatsApp ID"),
    caption: Optional[str] = Query(None, description="Optional file caption"),
    filename: Optional[str] = Query(None, description="Custom filename"),
    controller: FileController = Depends(get_file_controller),
) -> FileResponse:
    """
    Send a file from a local path.

    Args:
        session_name: Name of the WhatsApp session.
        file_path: Path to the local file.
        chat_id: WhatsApp ID.
        caption: Optional caption.
        filename: Optional custom filename.

    Returns:
        FileResponse with file details.
    """
    logger.info(f"Sending file {file_path} to {chat_id}")
    try:
        return await controller.send_file_from_path(
            session_name=session_name,
            chat_id=chat_id,
            file_path=Path(file_path),
            caption=caption,
            filename=filename,
        )
    except Exception as e:
        logger.error(f"Failed to send file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/send/{session_name}/upload",
    response_model=FileResponse,
    summary="Send uploaded file",
    description="Sends an uploaded file to a WhatsApp chat.",
)
async def send_uploaded_file(
    session_name: str,
    chat_id: str = Query(..., description="WhatsApp ID"),
    file: UploadFile = File(..., description="File to upload"),
    caption: Optional[str] = Query(None, description="Optional file caption"),
    controller: FileController = Depends(get_file_controller),
) -> FileResponse:
    """
    Send an uploaded file.

    Args:
        session_name: Name of the WhatsApp session.
        chat_id: WhatsApp ID.
        file: Uploaded file.
        caption: Optional caption.

    Returns:
        FileResponse with file details.
    """
    logger.info(f"Sending uploaded file {file.filename} to {chat_id}")
    try:
        return await controller.send_file_from_content(
            session_name=session_name,
            chat_id=chat_id,
            file_content=await file.read(),
            caption=caption,
            filename=file.filename,
        )
    except Exception as e:
        logger.error(f"Failed to send uploaded file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/send/{session_name}/url",
    response_model=FileResponse,
    summary="Send file from URL",
    description="Sends a file from a URL to a WhatsApp chat.",
)
async def send_file_from_url(
    session_name: str,
    file_url: str = Query(..., description="URL of the file to send"),
    chat_id: str = Query(..., description="WhatsApp ID"),
    caption: Optional[str] = Query(None, description="Optional file caption"),
    filename: Optional[str] = Query(None, description="Custom filename"),
    controller: FileController = Depends(get_file_controller),
) -> FileResponse:
    """
    Send a file from a URL.

    Args:
        session_name: Name of the WhatsApp session.
        file_url: URL of the file.
        chat_id: WhatsApp ID.
        caption: Optional caption.
        filename: Optional custom filename.

    Returns:
        FileResponse with file details.
    """
    logger.info(f"Sending file from URL {file_url} to {chat_id}")
    try:
        return await controller.send_file_from_url(
            session_name=session_name,
            chat_id=chat_id,
            file_url=file_url,
            caption=caption,
            filename=filename,
        )
    except Exception as e:
        logger.error(f"Failed to send file from URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/send/{session_name}/group",
    response_model=FileResponse,
    summary="Send file to group",
    description="Sends a file to a WhatsApp group.",
)
async def send_file_to_group(
    session_name: str,
    group_id: str = Query(..., description="WhatsApp group ID"),
    file: UploadFile = File(..., description="File to upload"),
    caption: Optional[str] = Query(None, description="Optional file caption"),
    controller: FileController = Depends(get_file_controller),
) -> FileResponse:
    """
    Send a file to a group.

    Args:
        session_name: Name of the WhatsApp session.
        group_id: WhatsApp group ID.
        file: Uploaded file.
        caption: Optional caption.

    Returns:
        FileResponse with file details.
    """
    logger.info(f"Sending file to group {group_id}")
    try:
        return await controller.send_file_to_group(
            session_name=session_name,
            group_id=group_id,
            file_content=await file.read(),
            caption=caption,
            filename=file.filename,
        )
    except Exception as e:
        logger.error(f"Failed to send file to group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/download/{session_name}/{message_id}",
    summary="Download a file",
    description="Downloads a file from a message.",
)
async def download_file(
    session_name: str,
    message_id: str,
    controller: FileController = Depends(get_file_controller),
) -> dict:
    """
    Download a file from a message.

    Args:
        session_name: Name of the WhatsApp session.
        message_id: ID of the message containing the file.

    Returns:
        Dictionary with file data (base64 encoded).
    """
    try:
        return await controller.download_file(
            session_name=session_name,
            message_id=message_id,
        )
    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/upload/{session_name}",
    summary="Upload file to Waha server",
    description="Uploads a file to the Waha server for later use.",
)
async def upload_file(
    session_name: str,
    file: UploadFile = File(..., description="File to upload"),
    controller: FileController = Depends(get_file_controller),
) -> dict:
    """
    Upload a file to the Waha server.

    Args:
        session_name: Name of the WhatsApp session.
        file: File to upload.

    Returns:
        Dictionary with upload result.
    """
    try:
        return await controller.upload_file(
            session_name=session_name,
            file=file,
        )
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
