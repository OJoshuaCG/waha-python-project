"""
WhatsApp-related Pydantic schemas.

This module defines all Pydantic models for API request and response handling.
These schemas provide data validation, serialization, and documentation
for the WhatsApp management API.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl


class SessionCreate(BaseModel):
    """
    Schema for creating a new WhatsApp session.

    Attributes:
        name: Unique name for the session.
        config: Optional session configuration.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique name for the WhatsApp session",
        examples=["my_whatsapp_session"],
    )
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional session configuration parameters",
    )


class SessionResponse(BaseModel):
    """
    Response schema for session operations.

    Attributes:
        id: Session identifier.
        name: Session name.
        status: Current session status.
        config: Session configuration.
        created_at: Session creation timestamp.
    """

    id: str = Field(..., description="Unique session identifier")
    name: str = Field(..., description="Session name")
    status: str = Field(..., description="Current session status")
    config: Optional[Dict[str, Any]] = Field(None, description="Session configuration")
    created_at: Optional[datetime] = Field(None, description="Session creation timestamp")


class SessionStatusResponse(BaseModel):
    """
    Detailed session status response.

    Attributes:
        session: Session details.
        connected: Whether WhatsApp is connected.
        phone: Connected phone number if available.
    """

    session: SessionResponse = Field(..., description="Session details")
    connected: bool = Field(..., description="Whether WhatsApp is connected")
    phone: Optional[str] = Field(None, description="Connected phone number")


class QRCodeResponse(BaseModel):
    """
    QR code response for authentication.

    Attributes:
        pairing_code: The QR code string.
        expires_at: When the QR code expires.
    """

    pairing_code: str = Field(..., description="QR code pairing string")
    expires_at: Optional[datetime] = Field(None, description="QR code expiration time")


class MessageSend(BaseModel):
    """
    Schema for sending a text message.

    Attributes:
        chat_id: WhatsApp ID (phone number or group ID).
        message: Message text to send.
        quoted_message_id: Optional message ID to reply to.
    """

    chat_id: str = Field(
        ...,
        description="WhatsApp ID (phone number or group ID)",
        examples=["1234567890", "1234567890@g.us"],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Message text content",
        examples=["Hello, this is a test message!"],
    )
    quoted_message_id: Optional[str] = Field(
        default=None,
        description="Optional ID of message to reply to",
    )


class MessageResponse(BaseModel):
    """
    Response schema for sent messages.

    Attributes:
        id: Unique message identifier.
        chat_id: Conversation ID.
        status: Message status.
        timestamp: When the message was sent.
    """

    id: str = Field(..., description="Unique message identifier")
    chat_id: str = Field(..., description="Conversation ID")
    status: str = Field(..., description="Message status")
    timestamp: datetime = Field(..., description="Message timestamp")


class FileSend(BaseModel):
    """
    Schema for sending files.

    Attributes:
        chat_id: WhatsApp ID (phone number or group ID).
        caption: Optional file caption.
        filename: Optional custom filename.
    """

    chat_id: str = Field(
        ...,
        description="WhatsApp ID (phone number or group ID)",
        examples=["1234567890", "1234567890@g.us"],
    )
    caption: Optional[str] = Field(
        default=None,
        max_length=1024,
        description="Optional caption for the file",
    )
    filename: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Custom filename for the file",
    )


class FileResponse(BaseModel):
    """
    Response schema for file operations.

    Attributes:
        id: Unique file identifier.
        chat_id: Conversation ID.
        status: Upload/send status.
        url: URL to access the file if applicable.
    """

    id: str = Field(..., description="Unique file identifier")
    chat_id: str = Field(..., description="Conversation ID")
    status: str = Field(..., description="File operation status")
    url: Optional[str] = Field(None, description="File URL if applicable")


class ChatResponse(BaseModel):
    """
    Schema representing a WhatsApp chat/conversation.

    Attributes:
        id: Unique chat identifier.
        name: Chat name.
        is_group: Whether this is a group chat.
        unread_count: Number of unread messages.
        last_message: Most recent message.
        last_message_time: When the last message was received.
    """

    id: str = Field(..., description="Unique chat identifier")
    name: str = Field(..., description="Chat name or contact name")
    is_group: bool = Field(default=False, description="Whether this is a group chat")
    unread_count: int = Field(default=0, description="Number of unread messages")
    last_message: Optional[str] = Field(None, description="Last message content")
    last_message_time: Optional[datetime] = Field(None, description="Last message timestamp")


class ChatMessagesRequest(BaseModel):
    """
    Request schema for retrieving chat messages.

    Attributes:
        chat_id: WhatsApp chat ID.
        limit: Maximum number of messages to retrieve.
    """

    chat_id: str = Field(
        ...,
        description="WhatsApp chat ID",
        examples=["1234567890", "1234567890@g.us"],
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of messages to retrieve",
    )


class GroupCreate(BaseModel):
    """
    Schema for creating a new WhatsApp group.

    Attributes:
        name: Group name.
        participants: List of phone numbers to add as participants.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name for the new WhatsApp group",
        examples=["My Test Group"],
    )
    participants: List[str] = Field(
        default_factory=list,
        description="List of phone numbers to add as participants",
        examples=["1234567890", "0987654321"],
    )


class GroupResponse(BaseModel):
    """
    Response schema for group operations.

    Attributes:
        id: Unique group identifier.
        name: Group name.
        description: Group description.
        participants: List of participant phone numbers.
        created_at: Group creation timestamp.
    """

    id: str = Field(..., description="Unique group identifier")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    participants: List[str] = Field(default_factory=list, description="Participant phone numbers")
    created_at: Optional[datetime] = Field(None, description="Group creation timestamp")


class WebhookConfig(BaseModel):
    """
    Schema for configuring webhooks.

    Attributes:
        url: Webhook URL.
        events: List of events to subscribe to.
    """

    url: HttpUrl = Field(
        ...,
        description="Webhook URL to receive events",
        examples=["https://example.com/webhook"],
    )
    events: List[str] = Field(
        default_factory=lambda: ["message", "session"],
        description="List of events to subscribe to",
    )


class HealthResponse(BaseModel):
    """
    Health check response schema.

    Attributes:
        status: Overall service status.
        waha_connected: Whether Waha server is reachable.
        timestamp: Check timestamp.
    """

    status: str = Field(..., description="Overall service status")
    waha_connected: bool = Field(..., description="Whether Waha server is reachable")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")


class ErrorResponse(BaseModel):
    """
    Standard error response schema.

    Attributes:
        error: Error type.
        message: Human-readable error message.
        details: Additional error details.
    """

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
