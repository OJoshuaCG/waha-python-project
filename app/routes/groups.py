"""
Group Routes Module.

This module defines API endpoints for managing WhatsApp groups.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.controllers.group_controller import GroupController
from app.schemas.whatsapp import (
    GroupCreate,
    GroupResponse,
    MessageResponse,
    ErrorResponse,
)
from app.utils.dependencies import get_group_controller
from app.utils.logger import logger

router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)


@router.post(
    "/create/{session_name}",
    response_model=GroupResponse,
    summary="Create a new group",
    description="Creates a new WhatsApp group with the specified name and participants.",
)
async def create_group(
    session_name: str,
    group_data: GroupCreate,
    controller: GroupController = Depends(get_group_controller),
) -> GroupResponse:
    """
    Create a new WhatsApp group.

    Args:
        session_name: Name of the WhatsApp session.
        group_data: Group creation parameters.

    Returns:
        GroupResponse with group details.
    """
    logger.info(f"Creating group: {group_data.name}")
    try:
        return await controller.create_group(session_name, group_data)
    except Exception as e:
        logger.error(f"Failed to create group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{session_name}",
    summary="List all groups",
    description="Retrieves all groups the session belongs to.",
)
async def get_groups(
    session_name: str,
    controller: GroupController = Depends(get_group_controller),
) -> list:
    """
    Get all groups.

    Args:
        session_name: Name of the WhatsApp session.

    Returns:
        List of group dictionaries.
    """
    try:
        return await controller.get_groups(session_name)
    except Exception as e:
        logger.error(f"Failed to get groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{session_name}/{group_id}",
    summary="Get group details",
    description="Retrieves details of a specific group.",
)
async def get_group_details(
    session_name: str,
    group_id: str,
    controller: GroupController = Depends(get_group_controller),
) -> dict:
    """
    Get group details.

    Args:
        session_name: Name of the WhatsApp session.
        group_id: WhatsApp group ID.

    Returns:
        Dictionary with group details.
    """
    try:
        return await controller.get_group_details(session_name, group_id)
    except Exception as e:
        logger.error(f"Failed to get group details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{session_name}/{group_id}/send",
    response_model=MessageResponse,
    summary="Send message to group",
    description="Sends a text message to a WhatsApp group.",
)
async def send_message_to_group(
    session_name: str,
    group_id: str,
    message: str = Query(..., description="Message text to send"),
    controller: GroupController = Depends(get_group_controller),
) -> MessageResponse:
    """
    Send a message to a group.

    Args:
        session_name: Name of the WhatsApp session.
        group_id: WhatsApp group ID.
        message: Message text to send.

    Returns:
        MessageResponse with message details.
    """
    logger.info(f"Sending message to group {group_id}")
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
    "/list/{session_name}",
    summary="List all groups (alias)",
    description="Retrieves all groups the session belongs to (alias for /{session_name}).",
)
async def list_my_groups(
    session_name: str,
    controller: GroupController = Depends(get_group_controller),
) -> list:
    """
    List all groups (alias).

    Args:
        session_name: Name of the WhatsApp session.

    Returns:
        List of group dictionaries.
    """
    try:
        return await controller.list_my_groups(session_name)
    except Exception as e:
        logger.error(f"Failed to list groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))
