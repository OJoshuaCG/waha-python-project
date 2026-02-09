"""
Message Controller Module.

This module handles all business logic related to WhatsApp messaging
operations including sending and receiving messages.
"""

from typing import Dict, List

from app.schemas.whatsapp import (
    ChatMessagesRequest,
    MessageResponse,
)
from app.utils.logger import logger
from app.utils.waha_client import WahaClient, WahaChat, WahaMessage


class MessageController:
    """
    Controller for managing WhatsApp messages and chats.

    This controller provides methods for sending messages, retrieving
    chat conversations, and managing message history.

    Attributes:
        waha_client: WahaClient instance for API communication.
    """

    def __init__(self, waha_client: WahaClient) -> None:
        """
        Initialize the message controller.

        Args:
            waha_client: WahaClient instance for making API calls.
        """
        self.waha_client = waha_client
        logger.info("MessageController initialized")

    async def send_message(
        self,
        session_name: str,
        chat_id: str,
        message: str,
        quoted_message_id: str = None,
    ) -> MessageResponse:
        """
        Send a text message to a WhatsApp chat or contact.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp ID (phone number or group ID).
            message: Message text to send.
            quoted_message_id: Optional ID of message to reply to.

        Returns:
            MessageResponse with message details.
        """
        logger.info(f"Sending message to {chat_id}")
        result = await self.waha_client.send_message(
            session_name=session_name,
            chat_id=chat_id,
            message=message,
            quoted_message_id=quoted_message_id,
        )
        return MessageResponse(
            id=result.get("id", ""),
            chat_id=chat_id,
            status=result.get("status", "sent"),
        )

    async def get_chats(
        self,
        session_name: str,
    ) -> List[Dict]:
        """
        Get all chats/conversations for a session.

        Args:
            session_name: Name of the session.

        Returns:
            List of chat dictionaries.
        """
        logger.info(f"Getting chats for session: {session_name}")
        chats = await self.waha_client.get_chats(session_name=session_name)
        return [
            {
                "id": chat.id,
                "name": chat.name,
                "is_group": chat.is_group,
                "unread_count": chat.unread_count,
                "last_message": chat.last_message,
                "last_message_time": chat.last_message_time,
            }
            for chat in chats
        ]

    async def get_chat_messages(
        self,
        session_name: str,
        chat_id: str,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Get messages from a specific chat.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp chat ID.
            limit: Maximum number of messages to retrieve.

        Returns:
            List of message dictionaries.
        """
        logger.info(f"Getting messages for chat: {chat_id}")
        messages = await self.waha_client.get_chat_messages(
            session_name=session_name,
            chat_id=chat_id,
            limit=limit,
        )
        return [
            {
                "id": msg.id,
                "conversation": msg.conversation,
                "sender": msg.sender,
                "message": msg.message,
                "timestamp": msg.timestamp,
                "type": msg.type,
                "from_me": msg.from_me,
            }
            for msg in messages
        ]

    async def delete_message(
        self,
        session_name: str,
        chat_id: str,
        message_id: str,
    ) -> Dict[str, str]:
        """
        Delete a message from a chat.

        Args:
            session_name: Name of the session.
            chat_id: WhatsApp chat ID.
            message_id: ID of the message to delete.

        Returns:
            Dictionary with status message.
        """
        logger.info(f"Deleting message {message_id} from {chat_id}")
        await self.waha_client.delete_message(
            session_name=session_name,
            chat_id=chat_id,
            message_id=message_id,
        )
        return {"status": "deleted", "message_id": message_id}

    async def send_message_to_group(
        self,
        session_name: str,
        group_id: str,
        message: str,
    ) -> MessageResponse:
        """
        Send a message to a WhatsApp group.

        Args:
            session_name: Name of the session.
            group_id: WhatsApp group ID.
            message: Message text to send.

        Returns:
            MessageResponse with message details.
        """
        logger.info(f"Sending message to group: {group_id}")
        result = await self.waha_client.send_message_to_group(
            session_name=session_name,
            group_id=group_id,
            message=message,
        )
        return MessageResponse(
            id=result.get("id", ""),
            chat_id=group_id,
            status=result.get("status", "sent"),
        )

    async def get_conversations(
        self,
        session_name: str,
    ) -> List[Dict]:
        """
        Get all conversations for a session (alias for get_chats).

        Args:
            session_name: Name of the session.

        Returns:
            List of conversation dictionaries.
        """
        return await self.get_chats(session_name=session_name)
