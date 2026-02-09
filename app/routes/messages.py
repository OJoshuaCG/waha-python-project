"""
Message Routes Module.

This module defines API endpoints for sending and receiving WhatsApp messages.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.controllers.message_controller import MessageController
from app.schemas.whatsapp import (
    MessageResponse,
    ChatMessagesRequest,
    ErrorResponse,
)
from app.utils.dependencies import get_message_controller
from app.utils.logger import logger

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)


@router.post(
    "/send/{session_name}",
    response_model=MessageResponse,
    summary="Send a text message",
    description="Sends a text message to a specified WhatsApp chat or contact.",
)
async def send_message(
    session_name: str,
    chat_id: str = Query(..., description="WhatsApp ID (phone number or group ID)"),
    message: str = Query(..., description="Message text to send"),
    quoted_message_id: Optional[str] = Query(None, description="Optional message ID to reply to"),
    controller: MessageController = Depends(get_message_controller),
) -> MessageResponse:
    """
    Send a text message to a WhatsApp chat or contact.

    Args:
        session_name: Name of the WhatsApp session.
        chat_id: WhatsApp ID (phone number or group ID).
        message: Message text to send.
        quoted_message_id: Optional ID of message to reply to.

    Returns:
        MessageResponse with message details.
    """
    logger.info(f"Sending message to {chat_id} via session {session_name}")
    try:
        return await controller.send_message(
            session_name=session_name,
            chat_id=chat_id,
            message=message,
            quoted_message_id=quoted_message_id,
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/chats/{session_name}",
    summary="Get all chats",
    description="Retrieves all chat conversations for a session.",
)
async def get_chats(
    session_name: str,
    controller: MessageController = Depends(get_message_controller),
) -> list:
    """
    Get all chat conversations.

    Args:
        session_name: Name of the WhatsApp session.

    Returns:
        List of chat dictionaries.
    """
    try:
        return await controller.get_chats(session_name)
    except Exception as e:
        logger.error(f"Failed to get chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/chats/{session_name}/{chat_id}",
    summary="Get chat messages",
    description="Retrieves messages from a specific chat.",
)
async def get_chat_messages(
    session_name: str,
    chat_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum messages to retrieve"),
    controller: MessageController = Depends(get_message_controller),
) -> list:
    """
    Get messages from a specific chat.

    Args:
        session_name: Name of the WhatsApp session.
        chat_id: WhatsApp chat ID.
        limit: Maximum number of messages to retrieve.

    Returns:
        List of message dictionaries.
    """
    try:
        return await controller.get_chat_messages(
            session_name=session_name,
            chat_id=chat_id,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Failed to get chat messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{session_name}/{chat_id}/{message_id}",
    summary="Delete a message",
    description="Deletes a message from a chat.",
)
async def delete_message(
    session_name: str,
    chat_id: str,
    message_id: str,
    controller: MessageController = Depends(get_message_controller),
) -> dict:
    """
    Delete a message from a chat.

    Args:
        session_name: Name of the WhatsApp session.
        chat_id: WhatsApp chat ID.
        message_id: ID of the message to delete.

    Returns:
        Status message.
    """
    try:
        return await controller.delete_message(
            session_name=session_name,
            chat_id=chat_id,
            message_id=message_id,
        )
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/groups/{session_name}/send",
    response_model=MessageResponse,
    summary="Send message to group",
    description="Sends a text message to a WhatsApp group.",
)
async def send_message_to_group(
    session_name: str,
    group_id: str = Query(..., description="WhatsApp group ID"),
    message: str = Query(..., description="Message text to send"),
    controller: MessageController = Depends(get_message_controller),
) -> MessageResponse:
    """
    Send a message to a WhatsApp group.

    Args:
        session_name: Name of the WhatsApp session.
        group_id: WhatsApp group ID.
        message: Message text to send.

    Returns:
        MessageResponse with message details.
    """
    logger.info(f"Sending message to group {group_id} via session {session_name}")
    try:
        return await controller.send_message_to_group(
            session_name=session_name,
            group_id=group_id,
            message=message,
        )
    except Exception as e:
        logger.error(f"Failed to send group message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/conversations/{session_name}",
    summary="Get all conversations",
    description="Retrieves all conversations for a session (alias for /chats).",
)
async def get_conversations(
    session_name: str,
    controller: MessageController = Depends(get_message_controller),
) -> list:
    """
    Get all conversations.

    Args:
        session_name: Name of the WhatsApp session.

    Returns:
        List of conversation dictionaries.
    """
    try:
        return await controller.get_conversations(session_name)
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
