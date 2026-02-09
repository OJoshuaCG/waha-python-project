"""
Health Check Routes Module.

This module defines API endpoints for health checks and monitoring.
"""

from datetime import datetime

from fastapi import APIRouter

from app.schemas.whatsapp import HealthResponse
from app.utils.logger import logger
from app.utils.waha_client import WahaClient

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Checks the health status of the API and Waha connection.",
)
async def health_check(waha_client: WahaClient) -> HealthResponse:
    """
    Check the health of the API and Waha connection.

    Returns:
        HealthResponse with status information.
    """
    waha_connected = await waha_client.ping()
    status = "healthy" if waha_connected else "degraded"

    logger.info(f"Health check: {status}")
    return HealthResponse(
        status=status,
        waha_connected=waha_connected,
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/live",
    summary="Liveness probe",
    description="Simple liveness check for container orchestration.",
)
async def liveness() -> dict:
    """
    Simple liveness check.

    Returns:
        Basic status message.
    """
    return {"status": "alive"}


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Checks if the service is ready to accept traffic.",
)
async def readiness(waha_client: WahaClient) -> dict:
    """
    Readiness check.

    Returns:
        Status message with Waha connection status.
    """
    waha_connected = await waha_client.ping()
    if waha_connected:
        return {"status": "ready", "waha": "connected"}
    return {"status": "not_ready", "waha": "disconnected"}
