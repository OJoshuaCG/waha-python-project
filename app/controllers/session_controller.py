"""
Session Controller Module.

This module handles all business logic related to WhatsApp session management
including connection, authentication, and session lifecycle operations.
"""

from typing import Dict, List, Optional

from app.schemas.whatsapp import (
    SessionCreate,
    SessionResponse,
    SessionStatusResponse,
    QRCodeResponse,
)
from app.utils.logger import logger
from app.utils.waha_client import WahaClient


class SessionController:
    """
    Controller for managing WhatsApp sessions.

    This controller provides a high-level interface for session operations
    including starting/stopping sessions, QR code authentication, and
    checking connection status.

    Attributes:
        waha_client: WahaClient instance for API communication.
    """

    def __init__(self, waha_client: WahaClient) -> None:
        """
        Initialize the session controller.

        Args:
            waha_client: WahaClient instance for making API calls.
        """
        self.waha_client = waha_client
        logger.info("SessionController initialized")

    async def start_session(
        self,
        session_data: SessionCreate,
    ) -> SessionResponse:
        """
        Start a new WhatsApp session.

        Args:
            session_data: Session creation parameters.

        Returns:
            SessionResponse with session details.
        """
        logger.info(f"Starting session: {session_data.name}")
        session = await self.waha_client.start_session(
            session_name=session_data.name,
            config=session_data.config,
        )
        return SessionResponse(
            id=session.id,
            name=session.name,
            status=session.status,
            config=session.config,
            created_at=session.created_at,
        )

    async def stop_session(
        self,
        session_name: str,
    ) -> Dict[str, str]:
        """
        Stop a running WhatsApp session.

        Args:
            session_name: Name of the session to stop.

        Returns:
            Dictionary with status message.
        """
        logger.info(f"Stopping session: {session_name}")
        await self.waha_client.stop_session(session_name=session_name)
        return {"status": "stopped", "session": session_name}

    async def get_session_status(
        self,
        session_name: str,
    ) -> SessionStatusResponse:
        """
        Get detailed status of a session.

        Args:
            session_name: Name of the session.

        Returns:
            SessionStatusResponse with detailed status.
        """
        logger.debug(f"Getting status for session: {session_name}")
        session = await self.waha_client.get_session_status(session_name=session_name)

        if session is None:
            return SessionStatusResponse(
                session=SessionResponse(
                    id=session_name,
                    name=session_name,
                    status="NOT_FOUND",
                ),
                connected=False,
                phone=None,
            )

        connected = session.status.upper() in ["STARTED", "CONNECTED", "READY"]
        return SessionStatusResponse(
            session=SessionResponse(
                id=session.id,
                name=session.name,
                status=session.status,
                config=session.config,
                created_at=session.created_at,
            ),
            connected=connected,
            phone=None,
        )

    async def get_qr_code(
        self,
        session_name: str,
    ) -> QRCodeResponse:
        """
        Get QR code for authentication.

        Args:
            session_name: Name of the session.

        Returns:
            QRCodeResponse with pairing code.
        """
        logger.info(f"Getting QR code for session: {session_name}")
        qr = await self.waha_client.get_qr_code(session_name=session_name)
        return QRCodeResponse(
            pairing_code=qr.pairing_code,
            expires_at=qr.expires_at,
        )

    async def get_qr_code_image(
        self,
        session_name: str,
    ) -> Dict[str, str]:
        """
        Get QR code as base64 image.

        Args:
            session_name: Name of the session.

        Returns:
            Dictionary with base64 image data.
        """
        logger.info(f"Getting QR code image for session: {session_name}")
        image_data = await self.waha_client.get_qr_code_image(session_name=session_name)
        return {"image": image_data}

    async def logout_session(
        self,
        session_name: str,
    ) -> Dict[str, str]:
        """
        Logout and delete a session.

        Args:
            session_name: Name of the session to logout.

        Returns:
            Dictionary with status message.
        """
        logger.info(f"Logging out session: {session_name}")
        await self.waha_client.logout_session(session_name=session_name)
        return {"status": "logged_out", "session": session_name}

    async def list_sessions(
        self,
    ) -> List[SessionResponse]:
        """
        List all sessions.

        Returns:
            List of SessionResponse objects.
        """
        logger.info("Listing all sessions")
        sessions = await self.waha_client.get_session_status(session_name="")
        if sessions is None:
            return []
        return [sessions.session]

    async def check_connection(
        self,
        session_name: str,
    ) -> Dict[str, bool]:
        """
        Check if WhatsApp is connected.

        Args:
            session_name: Name of the session.

        Returns:
            Dictionary with connection status.
        """
        session = await self.waha_client.get_session_status(session_name=session_name)
        connected = session is not None and session.status.upper() in [
            "STARTED",
            "CONNECTED",
            "READY",
        ]
        return {"connected": connected}
