"""
File Controller Module.

This module handles all business logic related to file operations
including sending and receiving files through WhatsApp.
"""

import base64
from pathlib import Path
from typing import Dict, Optional

from fastapi import UploadFile

from app.schemas.whatsapp import FileResponse
from app.utils.logger import logger
from app.utils.waha_client import WahaClient


class FileController:
    """
    Controller for managing WhatsApp file operations.

    This controller provides methods for sending and receiving files,
    including images, documents, and other media through WhatsApp.

    Attributes:
        waha_client: WahaClient instance for API communication.
    """

    def __init__(self, waha_client: WahaClient) -> None:
        """
        Initialize the file controller.

        Args:
            waha_client: WahaClient instance for making API calls.
        """
        self.waha_client = waha_client
        logger.info("FileController initialized")

    async def send_file_from_path(
        self,
        session_name: str,
        chat_id: str,
        file_path: Path,
        caption: str = "",
        filename: Optional[str] = None,
    ) -> FileResponse:
        """
        Send a file from a local path to a WhatsApp chat.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp ID (phone number or group ID).
            file_path: Path to the local file.
            caption: Optional caption for the file.
            filename: Optional custom filename.

        Returns:
            FileResponse with file details.
        """
        logger.info(f"Sending file {file_path} to {chat_id}")
        result = await self.waha_client.send_file(
            session_name=session_name,
            chat_id=chat_id,
            file_path=file_path,
            caption=caption,
            filename=filename,
        )
        return FileResponse(
            id=result.get("id", ""),
            chat_id=chat_id,
            status=result.get("status", "sent"),
            url=result.get("url"),
        )

    async def send_file_from_content(
        self,
        session_name: str,
        chat_id: str,
        file_content: bytes,
        caption: str = "",
        filename: Optional[str] = None,
    ) -> FileResponse:
        """
        Send a file from raw content bytes to a WhatsApp chat.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp ID (phone number or group ID).
            file_content: Raw file content as bytes.
            caption: Optional caption for the file.
            filename: Optional custom filename.

        Returns:
            FileResponse with file details.
        """
        logger.info(f"Sending file content to {chat_id}")
        result = await self.waha_client.send_file(
            session_name=session_name,
            chat_id=chat_id,
            file_content=file_content,
            caption=caption,
            filename=filename,
        )
        return FileResponse(
            id=result.get("id", ""),
            chat_id=chat_id,
            status=result.get("status", "sent"),
            url=result.get("url"),
        )

    async def send_file_from_url(
        self,
        session_name: str,
        chat_id: str,
        file_url: str,
        caption: str = "",
        filename: Optional[str] = None,
    ) -> FileResponse:
        """
        Send a file from a URL to a WhatsApp chat.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp ID (phone number or group ID).
            file_url: URL of the file to download and send.
            caption: Optional caption for the file.
            filename: Optional custom filename.

        Returns:
            FileResponse with file details.
        """
        logger.info(f"Sending file from URL {file_url} to {chat_id}")
        result = await self.waha_client.send_file(
            session_name=session_name,
            chat_id=chat_id,
            file_url=file_url,
            caption=caption,
            filename=filename,
        )
        return FileResponse(
            id=result.get("id", ""),
            chat_id=chat_id,
            status=result.get("status", "sent"),
            url=result.get("url"),
        )

    async def send_file_to_group(
        self,
        session_name: str,
        group_id: str,
        file_path: Optional[Path] = None,
        file_content: Optional[bytes] = None,
        file_url: Optional[str] = None,
        caption: str = "",
        filename: Optional[str] = None,
    ) -> FileResponse:
        """
        Send a file to a WhatsApp group.

        Args:
            session_name: Name of the session.
            group_id: WhatsApp group ID.
            file_path: Path to local file.
            file_content: Raw file content as bytes.
            file_url: URL of file to download and send.
            caption: Optional caption for the file.
            filename: Optional custom filename.

        Returns:
            FileResponse with file details.
        """
        logger.info(f"Sending file to group: {group_id}")
        result = await self.waha_client.send_file_to_group(
            session_name=session_name,
            group_id=group_id,
            file_path=file_path,
            file_content=file_content,
            file_url=file_url,
            caption=caption,
            filename=filename,
        )
        return FileResponse(
            id=result.get("id", ""),
            chat_id=group_id,
            status=result.get("status", "sent"),
            url=result.get("url"),
        )

    async def download_file(
        self,
        session_name: str,
        message_id: str,
    ) -> Dict[str, str]:
        """
        Download a file from a message.

        Args:
            session_name: Name of the session.
            message_id: ID of the message containing the file.

        Returns:
            Dictionary with file data (base64 encoded).
        """
        logger.info(f"Downloading file from message: {message_id}")
        file_content = await self.waha_client.download_file(
            session_name=session_name,
            message_id=message_id,
        )
        return {
            "file": base64.b64encode(file_content).decode("utf-8"),
            "message_id": message_id,
        }

    async def upload_file(
        self,
        session_name: str,
        file: UploadFile,
    ) -> Dict[str, str]:
        """
        Upload a file to the Waha server for later use.

        Args:
            session_name: Name of the session.
            file: UploadFile object from FastAPI.

        Returns:
            Dictionary with upload result.
        """
        logger.info(f"Uploading file: {file.filename}")
        content = await file.read()
        result = await self.waha_client.upload_file(
            session_name=session_name,
            file_content=content,
            filename=file.filename,
        )
        return result
