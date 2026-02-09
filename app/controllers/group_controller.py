"""
Group Controller Module.

This module handles all business logic related to WhatsApp group
operations including creating groups, sending messages, and managing
group participants.
"""

from typing import Dict, List

from app.schemas.whatsapp import (
    GroupCreate,
    GroupResponse,
    MessageResponse,
)
from app.utils.logger import logger
from app.utils.waha_client import WahaClient


class GroupController:
    """
    Controller for managing WhatsApp groups.

    This controller provides methods for creating groups, sending messages
    to groups, and managing group participants.

    Attributes:
        waha_client: WahaClient instance for API communication.
    """

    def __init__(self, waha_client: WahaClient) -> None:
        """
        Initialize the group controller.

        Args:
            waha_client: WahaClient instance for making API calls.
        """
        self.waha_client = waha_client
        logger.info("GroupController initialized")

    async def create_group(
        self,
        session_name: str,
        group_data: GroupCreate,
    ) -> GroupResponse:
        """
        Create a new WhatsApp group.

        Args:
            session_name: Name of the session.
            group_data: Group creation parameters.

        Returns:
            GroupResponse with group details.
        """
        logger.info(f"Creating group: {group_data.name}")
        group = await self.waha_client.create_group(
            session_name=session_name,
            group_name=group_data.name,
            participants=group_data.participants,
        )
        return GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            participants=group.participants,
            created_at=group.created_at,
        )

    async def get_groups(
        self,
        session_name: str,
    ) -> List[Dict]:
        """
        Get all groups the session is part of.

        Args:
            session_name: Name of the session.

        Returns:
            List of group dictionaries.
        """
        logger.info(f"Getting groups for session: {session_name}")
        groups = await self.waha_client.get_groups(session_name=session_name)
        return [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "participants": group.participants,
                "created_at": group.created_at,
            }
            for group in groups
        ]

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

    async def get_group_details(
        self,
        session_name: str,
        group_id: str,
    ) -> Dict:
        """
        Get details of a specific group.

        Args:
            session_name: Name of the session.
            group_id: WhatsApp group ID.

        Returns:
            Dictionary with group details.
        """
        logger.info(f"Getting details for group: {group_id}")
        groups = await self.waha_client.get_groups(session_name=session_name)
        for group in groups:
            if group.id == group_id:
                return {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                    "participants": group.participants,
                    "created_at": group.created_at,
                }
        return {"error": "Group not found"}

    async def list_my_groups(
        self,
        session_name: str,
    ) -> List[Dict]:
        """
        List all groups the session belongs to (alias for get_groups).

        Args:
            session_name: Name of the session.

        Returns:
            List of group dictionaries.
        """
        return await self.get_groups(session_name=session_name)
