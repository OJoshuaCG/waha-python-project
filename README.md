# WAHA FastAPI

FastAPI application for WhatsApp management using the WAHA (WhatsApp HTTP API) integration.

## Features

- **Session Management**: Start, stop, and manage WhatsApp sessions
- **QR Code Authentication**: Generate and retrieve QR codes for WhatsApp connection
- **Messaging**: Send and receive text messages to contacts and groups
- **File Operations**: Send and receive files (images, documents, etc.)
- **Group Management**: Create groups, send messages to groups
- **Health Checks**: Monitor API and Waha connection status

## Requirements

- Python 3.10+
- WAHA Server running (https://waha.devlike.pro/)
- uv (Python package manager)

## Installation

### 1. Install uv

If you haven't installed uv yet:

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```bash
cd backend
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# WAHA Server Configuration
WAHA_URL=http://localhost:3000
WAHA_API_KEY=your_api_key_if_required

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false

# Upload Configuration
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=52428800

# Logging
LOG_LEVEL=INFO
```

### 4. Start the Application

```bash
uv run python -m app.main
```

Or for development with auto-reload:

```bash
uv run python -m app.main --reload
```

## API Documentation

Once the application is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Quick Start Guide

### 1. Start a WhatsApp Session

```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{"name": "my_session", "config": {}}'
```

### 2. Get QR Code

```bash
curl -X GET "http://localhost:8000/api/v1/sessions/my_session/qr"
```

Scan the QR code with your WhatsApp app.

### 3. Check Connection Status

```bash
curl -X GET "http://localhost:8000/api/v1/sessions/my_session"
```

### 4. Send a Message

```bash
curl -X POST "http://localhost:8000/api/v1/messages/send/my_session" \
  -d "chat_id=1234567890" \
  -d "message=Hello from WAHA FastAPI!"
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Configuration management
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── session_controller.py   # Session management logic
│   │   ├── message_controller.py  # Messaging logic
│   │   ├── file_controller.py     # File operations logic
│   │   └── group_controller.py    # Group management logic
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── session.py             # Session endpoints
│   │   ├── messages.py            # Message endpoints
│   │   ├── files.py               # File endpoints
│   │   ├── groups.py              # Group endpoints
│   │   └── health.py              # Health check endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── whatsapp.py            # Pydantic models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── waha_client.py         # WAHA API client
│   │   ├── logger.py              # Logging configuration
│   │   └── dependencies.py        # Dependency injection
│   └── uploads/                   # Uploaded files directory
├── tests/                          # Test files
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WAHA_URL` | WAHA server URL | `http://localhost:3000` |
| `WAHA_API_KEY` | WAHA API key (if required) | `None` |
| `APP_HOST` | FastAPI server host | `0.0.0.0` |
| `APP_PORT` | FastAPI server port | `8000` |
| `APP_DEBUG` | Enable debug mode | `false` |
| `UPLOAD_DIR` | Upload directory | `./uploads` |
| `MAX_UPLOAD_SIZE` | Max file upload size (bytes) | `52428800` (50MB) |
| `LOG_LEVEL` | Logging level | `INFO` |

## API Endpoints

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sessions` | Start a new session |
| POST | `/api/v1/sessions/{name}/stop` | Stop a session |
| GET | `/api/v1/sessions/{name}` | Get session status |
| GET | `/api/v1/sessions/{name}/qr` | Get QR code |
| GET | `/api/v1/sessions/{name}/qr/image` | Get QR code image |
| DELETE | `/api/v1/sessions/{name}` | Logout and delete session |
| GET | `/api/v1/sessions/{name}/connected` | Check connection |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/messages/send/{session}` | Send a message |
| GET | `/api/v1/messages/chats/{session}` | Get all chats |
| GET | `/api/v1/messages/chats/{session}/{chat_id}` | Get chat messages |
| DELETE | `/api/v1/messages/{session}/{chat_id}/{message_id}` | Delete a message |
| POST | `/api/v1/messages/groups/{session}/send` | Send message to group |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/files/send/{session}/path` | Send file from path |
| POST | `/api/v1/files/send/{session}/upload` | Send uploaded file |
| POST | `/api/v1/files/send/{session}/url` | Send file from URL |
| POST | `/api/v1/files/send/{session}/group` | Send file to group |
| GET | `/api/v1/files/download/{session}/{message_id}` | Download a file |
| POST | `/api/v1/files/upload/{session}` | Upload file to WAHA |

### Groups

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/groups/create/{session}` | Create a new group |
| GET | `/api/v1/groups/{session}` | List all groups |
| GET | `/api/v1/groups/{session}/{group_id}` | Get group details |
| POST | `/api/v1/groups/{session}/{group_id}/send` | Send message to group |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/health/live` | Liveness probe |
| GET | `/health/ready` | Readiness probe |

## License

MIT License
