"""
WAHA FastAPI Application.

This is the main entry point for the WhatsApp management API.
It provides a comprehensive interface for managing WhatsApp sessions,
sending/receiving messages, handling groups, and file operations.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routes import (
    session_router,
    messages_router,
    files_router,
    groups_router,
    health_router,
)
from app.utils.logger import logger
from app.utils.waha_client import WahaClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    logger.info("Starting WAHA FastAPI Application...")
    logger.info(f"WAHA URL: {settings.WAHA_URL}")

    waha_client = WahaClient()
    connected = await waha_client.ping()

    if connected:
        logger.info("Successfully connected to Waha server")
    else:
        logger.warning("Waha server not reachable - please ensure WAHA is running")

    yield

    logger.info("Shutting down WAHA FastAPI Application...")
    await waha_client.close()


app = FastAPI(
    title="WAHA FastAPI",
    description="""
    ## WhatsApp Management API

    This API provides a comprehensive interface for managing WhatsApp through
    the WAHA (WhatsApp HTTP API) integration.

    ### Features

    - **Session Management**: Start, stop, and manage WhatsApp sessions
    - **QR Code Authentication**: Generate and retrieve QR codes for WhatsApp connection
    - **Messaging**: Send and receive text messages
    - **File Operations**: Send and receive files (images, documents, etc.)
    - **Group Management**: Create groups, send messages to groups
    - **Health Checks**: Monitor API and Waha connection status

    ### Usage

    1. Start a session with a unique name
    2. Get the QR code and scan it with WhatsApp
    3. Wait for connection confirmation
    4. Start sending messages and managing groups

    ### API Documentation

    - Swagger UI: `/docs`
    - ReDoc: `/redoc`
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(session_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(groups_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.

    Args:
        request: The incoming request.
        exc: The exception that was raised.

    Returns:
        JSONResponse with error details.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.APP_DEBUG else None,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )
