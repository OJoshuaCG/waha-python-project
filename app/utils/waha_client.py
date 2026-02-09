"""
Waha API Client Module.

This module provides a comprehensive client for interacting with the Waha
(WhatsApp HTTP API) server. It handles all communication with the Waha
API including session management, QR code authentication, messaging,
and file operations.

The client is designed to be async-compatible and integrates seamlessly
with FastAPI's async ecosystem.
"""

import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.utils.logger import logger


class WahaSession(BaseModel):
    """
    Represents a Waha session with its configuration and state.

    Attributes:
        id: Unique session identifier.
        name: Human-readable session name.
        status: Current session status (STARTED, STOPPED, SCANNING, etc.).
        config: Session configuration dictionary.
        created_at: Session creation timestamp.
        updated_at: Last update timestamp.
    """

    id: str = Field(..., description="Unique session identifier")
    name: str = Field(..., description="Human-readable session name")
    status: str = Field(..., description="Current session status")
    config: Dict[str, Any] = Field(default_factory=dict, description="Session configuration")
    created_at: Optional[datetime] = Field(None, description="Session creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class QRCodeResponse(BaseModel):
    """
    Response model for QR code generation requests.

    Attributes:
        pairing_code: The QR code string for pairing.
        expires_at: When the QR code expires.
    """

    pairing_code: str = Field(..., description="QR code string for pairing")
    expires_at: Optional[datetime] = Field(None, description="QR code expiration time")


class WahaMessage(BaseModel):
    """
    Represents a WhatsApp message.

    Attributes:
        id: Unique message identifier.
        conversation: Conversation/chat ID.
        sender: Sender phone number or ID.
        message: Message content.
        timestamp: When the message was sent/received.
        type: Message type (text, image, file, etc.).
        from_me: Whether the message was sent by us.
    """

    id: str = Field(..., description="Unique message identifier")
    conversation: str = Field(..., description="Conversation/chat ID")
    sender: str = Field(..., description="Sender phone number or ID")
    message: str = Field(default="", description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    type: str = Field(default="text", description="Message type")
    from_me: bool = Field(default=False, description="Whether message was sent by us")


class WahaChat(BaseModel):
    """
    Represents a WhatsApp chat/conversation.

    Attributes:
        id: Unique chat identifier.
        name: Chat name (contact or group name).
        is_group: Whether this is a group chat.
        unread_count: Number of unread messages.
        last_message: The most recent message in the chat.
        last_message_time: When the last message was received.
    """

    id: str = Field(..., description="Unique chat identifier")
    name: str = Field(..., description="Chat name")
    is_group: bool = Field(default=False, description="Whether this is a group chat")
    unread_count: int = Field(default=0, description="Number of unread messages")
    last_message: Optional[str] = Field(None, description="Last message content")
    last_message_time: Optional[datetime] = Field(None, description="Last message timestamp")


class WahaGroup(BaseModel):
    """
    Represents a WhatsApp group.

    Attributes:
        id: Unique group identifier.
        name: Group name.
        description: Group description.
        participants: List of participant phone numbers.
        created_at: When the group was created.
    """

    id: str = Field(..., description="Unique group identifier")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    participants: List[str] = Field(default_factory=list, description="Participant phone numbers")
    created_at: Optional[datetime] = Field(None, description="Group creation timestamp")


class WahaClient:
    """
    Async client for communicating with the Waha (WhatsApp HTTP API) server.

    This client provides methods for:
    - Session management (start, stop, check status)
    - QR code authentication
    - Sending and receiving messages
    - Managing groups
    - File operations (send/receive files)

    Example:
        ```python
        client = WahaClient()
        await client.start_session("my_session")
        qr_code = await client.get_qr_code("my_session")
        await client.send_message("my_session", "1234567890", "Hello!")
        ```

    Attributes:
        base_url: Base URL of the Waha server.
        api_key: Optional API key for authentication.
        http_client: Shared httpx.AsyncClient instance.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize the Waha client.

        Args:
            base_url: Base URL of the Waha server. Defaults to settings.WAHA_URL.
            api_key: Optional API key for Waha authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url or settings.WAHA_URL.rstrip("/")
        self.api_key = api_key or settings.WAHA_API_KEY
        self.timeout = timeout
        self.http_client: Optional[httpx.AsyncClient] = None
        logger.info(f"WahaClient initialized with base URL: {self.base_url}")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers including authentication if configured.

        Returns:
            Dictionary of HTTP headers.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create the async HTTP client.

        Returns:
            httpx.AsyncClient instance.
        """
        if self.http_client is None or self.http_client.is_closed:
            self.http_client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self._get_headers(),
            )
        return self.http_client

    async def close(self) -> None:
        """
        Close the HTTP client connection.
        """
        if self.http_client and not self.http_client.is_closed:
            await self.http_client.aclose()
            self.http_client = None
            logger.info("WahaClient HTTP connection closed")

    async def __aenter__(self) -> "WahaClient":
        """
        Async context manager entry.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Async context manager exit.
        """
        await self.close()

    async def ping(self) -> bool:
        """
        Check if the Waha server is reachable.

        Returns:
            True if server is reachable, False otherwise.
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/ping")
            response.raise_for_status()
            logger.info("Waha server ping successful")
            return True
        except Exception as e:
            logger.error(f"Waha server ping failed: {e}")
            return False

    async def get_version(self) -> Dict[str, Any]:
        """
        Get the Waha server version information.

        Returns:
            Dictionary containing version information.
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/version")
            response.raise_for_status()
            logger.debug("Waha version retrieved successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get Waha version: {e}")
            raise

    async def start_session(
        self,
        session_name: str = "default",
        config: Optional[Dict[str, Any]] = None,
    ) -> WahaSession:
        """
        Start a new or existing WhatsApp session.

        Args:
            session_name: Name for the session.
            config: Optional session configuration.

        Returns:
            WahaSession object with session details.
        """
        try:
            client = await self._get_client()
            payload = {
                "name": session_name,
                "config": config or {},
            }
            response = await client.post(
                f"{self.base_url}/api/sessions/start",
                json=payload,
            )
            response.raise_for_status()
            session_data = response.json()
            logger.info(f"Session '{session_name}' started successfully")
            return WahaSession(**session_data)
        except Exception as e:
            logger.error(f"Failed to start session '{session_name}': {e}")
            raise

    async def stop_session(self, session_name: str = "default") -> Dict[str, Any]:
        """
        Stop a running WhatsApp session.

        Args:
            session_name: Name of the session to stop.

        Returns:
            Dictionary containing the response.
        """
        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/api/sessions/stop/{session_name}",
            )
            response.raise_for_status()
            logger.info(f"Session '{session_name}' stopped successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to stop session '{session_name}': {e}")
            raise

    async def get_session_status(self, session_name: str = "default") -> Optional[WahaSession]:
        """
        Get the current status of a session.

        Args:
            session_name: Name of the session.

        Returns:
            WahaSession object or None if not found.
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url}/api/sessions/{session_name}",
            )
            if response.status_code == 404:
                logger.warning(f"Session '{session_name}' not found")
                return None
            response.raise_for_status()
            return WahaSession(**response.json())
        except Exception as e:
            logger.error(f"Failed to get session status: {e}")
            raise

    async def get_qr_code(self, session_name: str = "default") -> QRCodeResponse:
        """
        Get the QR code for authentication.

        Args:
            session_name: Name of the session.

        Returns:
            QRCodeResponse with pairing code.

        Raises:
            Exception: If QR code generation fails.
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url}/api/sessions/{session_name}/qr",
            )
            response.raise_for_status()
            qr_data = response.json()
            logger.info(f"QR code generated for session '{session_name}'")
            return QRCodeResponse(**qr_data)
        except Exception as e:
            logger.error(f"Failed to get QR code: {e}")
            raise

    async def get_qr_code_image(self, session_name: str = "default") -> str:
        """
        Get the QR code as a base64-encoded image.

        Args:
            session_name: Name of the session.

        Returns:
            Base64-encoded QR code image.
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url}/api/sessions/{session_name}/qr-image",
            )
            response.raise_for_status()
            data = response.json()
            return data.get("image", "")
        except Exception as e:
            logger.error(f"Failed to get QR code image: {e}")
            raise

    async def logout_session(self, session_name: str = "default") -> Dict[str, Any]:
        """
        Logout and delete a session.

        Args:
            session_name: Name of the session to logout.

        Returns:
            Dictionary containing the response.
        """
        try:
            client = await self._get_client()
            response = await client.delete(
                f"{self.base_url}/api/sessions/{session_name}",
            )
            response.raise_for_status()
            logger.info(f"Session '{session_name}' logged out successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to logout session: {e}")
            raise

    async def send_message(
        self,
        session_name: str = "default",
        chat_id: str = "",
        message: str = "",
        quoted_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a text message to a chat or contact.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp ID (phone number or group ID).
            message: Message text to send.
            quoted_message_id: Optional ID of message to reply to.

        Returns:
            Dictionary containing the message response.
        """
        try:
            client = await self._get_client()
            payload: Dict[str, Any] = {
                "chatId": chat_id,
                "message": message,
            }
            if quoted_message_id:
                payload["quotedMessageId"] = quoted_message_id

            response = await client.post(
                f"{self.base_url}/api/sessions/{session_name}/send/text",
                json=payload,
            )
            response.raise_for_status()
            logger.info(f"Message sent to {chat_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def send_file(
        self,
        session_name: str = "default",
        chat_id: str = "",
        file_path: Optional[Path] = None,
        file_content: Optional[bytes] = None,
        file_url: Optional[str] = None,
        caption: str = "",
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a file to a chat or contact.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp ID (phone number or group ID).
            file_path: Path to local file to send.
            file_content: Raw file content as bytes.
            file_url: URL of file to download and send.
            caption: Optional caption for the file.
            filename: Custom filename for the file.

        Returns:
            Dictionary containing the file send response.
        """
        try:
            client = await self._get_client()

            if file_path:
                with open(file_path, "rb") as f:
                    file_content = f.read()

            if file_content:
                files = {"file": (filename or "file", file_content)}
                data = {"chatId": chat_id}
                if caption:
                    data["caption"] = caption

                response = await client.post(
                    f"{self.base_url}/api/sessions/{session_name}/send/file",
                    files=files,
                    data=data,
                )
            elif file_url:
                payload = {
                    "chatId": chat_id,
                    "url": file_url,
                    "caption": caption,
                    "filename": filename,
                }
                response = await client.post(
                    f"{self.base_url}/api/sessions/{session_name}/send/file",
                    json=payload,
                )
            else:
                raise ValueError("Must provide file_path, file_content, or file_url")

            response.raise_for_status()
            logger.info(f"File sent to {chat_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send file: {e}")
            raise

    async def upload_file(
        self,
        session_name: str = "default",
        file_path: Optional[Path] = None,
        file_content: Optional[bytes] = None,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file to Waha server for later sending.

        Args:
            session_name: Name of the session.
            file_path: Path to local file.
            file_content: Raw file content as bytes.
            filename: Custom filename.

        Returns:
            Dictionary containing the upload response with file ID.
        """
        try:
            client = await self._get_client()

            if file_path:
                with open(file_path, "rb") as f:
                    file_content = f.read()

            if file_content:
                files = {"file": (filename or "file", file_content)}
                response = await client.post(
                    f"{self.base_url}/api/sessions/{session_name}/files/upload",
                    files=files,
                )
            else:
                raise ValueError("Must provide file_path or file_content")

            response.raise_for_status()
            logger.info(f"File uploaded successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    async def download_file(
        self,
        session_name: str = "default",
        message_id: str = "",
    ) -> bytes:
        """
        Download a file from a message.

        Args:
            session_name: Name of the session.
            message_id: ID of the message containing the file.

        Returns:
            Raw file content as bytes.
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url}/api/sessions/{session_name}/messages/{message_id}/download",
            )
            response.raise_for_status()
            logger.info(f"File downloaded: {message_id}")
            return response.content
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise

    async def get_chats(self, session_name: str = "default") -> List[WahaChat]:
        """
        Get all chats/conversations for a session.

        Args:
            session_name: Name of the session.

        Returns:
            List of WahaChat objects.
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url}/api/sessions/{session_name}/chats",
            )
            response.raise_for_status()
            chats_data = response.json()
            logger.info(f"Retrieved {len(chats_data)} chats")
            return [WahaChat(**chat) for chat in chats_data]
        except Exception as e:
            logger.error(f"Failed to get chats: {e}")
            raise

    async def get_chat_messages(
        self,
        session_name: str = "default",
        chat_id: str = "",
        limit: int = 50,
    ) -> List[WahaMessage]:
        """
        Get messages from a specific chat.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp chat ID.
            limit: Maximum number of messages to retrieve.

        Returns:
            List of WahaMessage objects.
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url}/api/sessions/{session_name}/chats/{chat_id}",
                params={"limit": limit},
            )
            response.raise_for_status()
            messages_data = response.json()
            logger.info(f"Retrieved {len(messages_data)} messages from {chat_id}")
            return [WahaMessage(**msg) for msg in messages_data]
        except Exception as e:
            logger.error(f"Failed to get chat messages: {e}")
            raise

    async def get_groups(self, session_name: str = "default") -> List[WahaGroup]:
        """
        Get all groups the session is part of.

        Args:
            session_name: Name of the session.

        Returns:
            List of WahaGroup objects.
        """
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url}/api/sessions/{session_name}/groups",
            )
            response.raise_for_status()
            groups_data = response.json()
            logger.info(f"Retrieved {len(groups_data)} groups")
            return [WahaGroup(**group) for group in groups_data]
        except Exception as e:
            logger.error(f"Failed to get groups: {e}")
            raise

    async def create_group(
        self,
        session_name: str = "default",
        group_name: str = "",
        participants: Optional[List[str]] = None,
    ) -> WahaGroup:
        """
        Create a new WhatsApp group.

        Args:
            session_name: Name of the session.
            group_name: Name for the new group.
            participants: List of phone numbers to add.

        Returns:
            WahaGroup object for the created group.
        """
        try:
            client = await self._get_client()
            payload = {
                "name": group_name,
                "participants": participants or [],
            }
            response = await client.post(
                f"{self.base_url}/api/sessions/{session_name}/groups",
                json=payload,
            )
            response.raise_for_status()
            group_data = response.json()
            logger.info(f"Group '{group_name}' created successfully")
            return WahaGroup(**group_data)
        except Exception as e:
            logger.error(f"Failed to create group: {e}")
            raise

    async def send_message_to_group(
        self,
        session_name: str = "default",
        group_id: str = "",
        message: str = "",
    ) -> Dict[str, Any]:
        """
        Send a message to a group.

        Args:
            session_name: Name of the session.
            group_id: WhatsApp group ID.
            message: Message text to send.

        Returns:
            Dictionary containing the message response.
        """
        return await self.send_message(
            session_name=session_name,
            chat_id=group_id,
            message=message,
        )

    async def send_file_to_group(
        self,
        session_name: str = "default",
        group_id: str = "",
        file_path: Optional[Path] = None,
        file_content: Optional[bytes] = None,
        file_url: Optional[str] = None,
        caption: str = "",
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a file to a group.

        Args:
            session_name: Name of the session.
            group_id: WhatsApp group ID.
            file_path: Path to local file to send.
            file_content: Raw file content as bytes.
            file_url: URL of file to download and send.
            caption: Optional caption for the file.
            filename: Custom filename for the file.

        Returns:
            Dictionary containing the file send response.
        """
        return await self.send_file(
            session_name=session_name,
            chat_id=group_id,
            file_path=file_path,
            file_content=file_content,
            file_url=file_url,
            caption=caption,
            filename=filename,
        )

    async def delete_message(
        self,
        session_name: str = "default",
        chat_id: str = "",
        message_id: str = "",
    ) -> Dict[str, Any]:
        """
        Delete a message from a chat.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp chat ID.
            message_id: ID of the message to delete.

        Returns:
            Dictionary containing the response.
        """
        try:
            client = await self._get_client()
            payload = {
                "chatId": chat_id,
                "messageId": message_id,
            }
            response = await client.delete(
                f"{self.base_url}/api/sessions/{session_name}/messages",
                json=payload,
            )
            response.raise_for_status()
            logger.info(f"Message {message_id} deleted from {chat_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            raise
