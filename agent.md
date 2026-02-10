# 🤖 AI Agent Guide: WhatsPlay Project

## Project Identity
**WhatsPlay** is a production-ready FastAPI wrapper for WAHA (WhatsApp HTTP API). It provides a clean, typed, and secure interface for WhatsApp automation through session management, messaging, and file operations.

---

## Tech Stack & Dependencies

### Core Technologies
- **Language**: Python 3.12+
- **Framework**: FastAPI 0.115.6
- **Package Manager**: `uv` (Astral's ultra-fast package manager)
- **HTTP Client**: `httpx` (async)
- **Validation**: Pydantic v2
- **Logging**: Loguru
- **Containerization**: Docker + Docker Compose

### Key Libraries
- `python-dotenv`: Environment configuration
- `uvicorn`: ASGI server
- `python-multipart`: File upload support

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point, lifespan management
│   ├── core/
│   │   └── config.py        # Pydantic Settings (env vars)
│   ├── controllers/         # Business logic layer
│   │   ├── session_controller.py
│   │   ├── message_controller.py
│   │   ├── file_controller.py
│   │   └── group_controller.py
│   ├── routes/              # API endpoints (thin layer)
│   │   ├── session.py
│   │   ├── messages.py
│   │   ├── files.py
│   │   ├── groups.py
│   │   └── health.py
│   ├── schemas/             # Pydantic models for request/response
│   │   └── whatsapp.py
│   └── utils/               # Shared utilities
│       ├── waha_client.py   # WAHA API client (critical)
│       ├── dependencies.py  # FastAPI dependency injection
│       └── logger.py        # Logging configuration
├── docs/                    # Technical documentation
├── Dockerfile               # Multi-stage build with uv
├── docker-compose.yml       # Orchestration (backend + WAHA)
├── pyproject.toml           # Dependencies (uv format)
├── uv.lock                  # Locked dependencies
└── agent.md                 # This file
```

---

## Critical Architecture Notes

### 1. WAHA Integration Specifics
**Authentication**:
- WAHA uses a **custom header** for API authentication: `X-Api-Key`
- **NOT** `Authorization: Bearer` (common mistake)
- The key must match between:
  - Backend: `WAHA_API_KEY` env var
  - WAHA Server: `WAHA_API_KEY` env var

**Session Management**:
- To create AND start a session: `POST /api/sessions` with body `{"name": "session_name", "config": {}}`
- **Do NOT use** `/api/sessions/start` unless the session already exists but is stopped
- Session lifecycle: `STOPPED` → `STARTING` → `SCAN_QR_CODE` → `WORKING`

**Engine**:
- Default engine: `WEBJS` (WhatsApp Web via Puppeteer/Chromium)
- Configured in `docker-compose.yml`: `WHATSAPP_DEFAULT_ENGINE=WEBJS`

### 2. Docker Architecture
**Service Dependencies**:
```yaml
backend:
  depends_on:
    waha:
      condition: service_healthy
```
- Backend waits for WAHA to be healthy before starting
- Internal DNS: Backend communicates with WAHA via `http://waha:3000`
- External access: `localhost:8000` (backend), `localhost:3000` (WAHA)

**Multi-stage Dockerfile**:
- Stage 1 (builder): Uses `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` to sync dependencies
- Stage 2 (runtime): Copies virtual environment, runs as non-root user `appuser`
- Pre-creates `/app/logs` and `/app/uploads` with correct permissions

### 3. Code Patterns & Conventions

**Dependency Injection**:
```python
# In routes/session.py
async def start_session(
    session_data: SessionCreate,
    controller: SessionController = Depends(get_session_controller),
):
    return await controller.start_session(session_data)
```

**Controller Pattern**:
- Controllers orchestrate business logic
- They receive injected `WahaClient` instances
- Keep routes thin (validation + delegation only)

**Error Handling**:
- Controllers catch exceptions and log them
- Routes convert exceptions to HTTP exceptions
- WAHA client raises `httpx.HTTPStatusError` on API errors

---

## Environment Variables

### Required Variables
| Variable | Description | Docker Value | Local Value |
|----------|-------------|--------------|-------------|
| `WAHA_URL` | WAHA server URL | `http://waha:3000` | `http://localhost:3000` |
| `WAHA_API_KEY` | Shared secret key | `plataforma_waha_secret_key` | Same as WAHA |
| `APP_HOST` | FastAPI bind address | `0.0.0.0` | `0.0.0.0` |
| `APP_PORT` | FastAPI port | `8000` | `8000` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `APP_DEBUG` | Enable debug mode | `false` |
| `UPLOAD_DIR` | File upload directory | `./uploads` |
| `MAX_UPLOAD_SIZE` | Max upload size (bytes) | `52428800` (50MB) |
| `LOG_LEVEL` | Logging level | `INFO` |

---

## Common Agent Commands

### Development
```bash
# Sync dependencies
uv sync

# Run locally (development mode with auto-reload)
uv run python -m app.main

# Run tests (if implemented)
uv run pytest
```

### Docker Operations
```bash
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker logs waha-server

# Restart specific service
docker-compose restart backend

# Stop all services
docker-compose down

# Clean rebuild (removes volumes)
docker-compose down -v && docker-compose up -d --build
```

### Debugging
```bash
# Check container status
docker ps

# Inspect backend health
curl http://localhost:8000/health

# Inspect WAHA health
curl http://localhost:3000/ping

# View WAHA API docs
# Open browser: http://localhost:3000/docs
```

---

## Troubleshooting Guide for Agents

### Error: 401 Unauthorized
**Symptom**: `Client error '401 Unauthorized' for url 'http://waha:3000/api/sessions'`

**Root Cause**: API key mismatch or incorrect header format

**Solution**:
1. Verify `WAHA_API_KEY` is identical in both services (docker-compose.yml)
2. Check `app/utils/waha_client.py` uses `X-Api-Key` header (NOT `Authorization`)
3. Restart services: `docker-compose restart`

### Error: 422 Unprocessable Entity
**Symptom**: `Client error '422 Unprocessable Entity' for url 'http://waha:3000/api/sessions/start'`

**Root Cause**: Trying to start a non-existent session OR using wrong endpoint

**Solution**:
1. Use `POST /api/sessions` to create AND start (not `/api/sessions/start`)
2. Ensure request body has `{"name": "session_name"}` at minimum
3. Check WAHA logs for validation errors: `docker logs waha-server --tail 50`

### Error: Permission Denied (logs)
**Symptom**: `PermissionError: [Errno 13] Permission denied: 'logs'`

**Root Cause**: Dockerfile doesn't create log directory before switching to non-root user

**Solution**:
1. Verify Dockerfile has:
   ```dockerfile
   RUN mkdir -p /app/logs /app/uploads && \
       chown -R appuser:appuser /app/logs /app/uploads
   ```
2. Rebuild: `docker-compose up -d --build`

### Error: Backend Container Restarting
**Symptom**: `docker ps` shows `Restarting (1) X seconds ago`

**Root Cause**: Application crash on startup (usually import errors or permission issues)

**Solution**:
1. Check logs: `docker logs waha-fastapi-backend`
2. Look for Python tracebacks
3. Common causes:
   - Missing dependencies (rebuild image)
   - Permission issues (check Dockerfile)
   - Port already in use (stop conflicting processes)

### Error: Port Already in Use
**Symptom**: `failed to bind host port for 0.0.0.0:3000`

**Root Cause**: Another WAHA instance or process using port 3000/8000

**Solution**:
```bash
# Find and stop conflicting containers
docker ps -a | grep waha
docker stop <container_id> && docker rm <container_id>

# On Windows, kill Python processes if running locally
Stop-Process -Name python -Force
```

### Session Stuck in STARTING
**Symptom**: Session status never progresses to `SCAN_QR_CODE`

**Root Cause**: WAHA engine initialization issue

**Solution**:
1. Wait 15-20 seconds (Chromium startup time)
2. Check WAHA logs for errors: `docker logs waha-server`
3. Restart WAHA: `docker-compose restart waha`
4. If persistent, delete session and recreate

---

## API Quick Reference

### Session Endpoints (WhatsPlay)
- `POST /api/v1/sessions` - Create and start session
- `GET /api/v1/sessions/{name}` - Get session status
- `GET /api/v1/sessions/{name}/qr/image` - Get QR code (Base64)
- `DELETE /api/v1/sessions/{name}` - Stop and delete session

### Message Endpoints
- `POST /api/v1/messages/send/{session_name}?chat_id=X&message=Y`
- `GET /api/v1/messages/chats/{session_name}` - List chats

### File Endpoints
- `POST /api/v1/files/send/{session_name}/upload` - Upload and send file
- `POST /api/v1/files/send/{session_name}/url` - Send file from URL

---

## Code Modification Guidelines

### When Adding New Endpoints
1. Create schema in `app/schemas/whatsapp.py`
2. Add method to appropriate controller
3. Create route in `app/routes/`
4. Register router in `app/main.py` if new file
5. Update this agent.md with new endpoint

### When Modifying WAHA Client
1. **Always** check WAHA documentation: https://waha.devlike.pro/docs/
2. Verify endpoint URL structure (common mistake: `/api/sessions/start` vs `/api/sessions`)
3. Test authentication header format
4. Update type hints and docstrings
5. Handle errors gracefully (log + raise)

### When Changing Docker Configuration
1. Update both `Dockerfile` and `docker-compose.yml` if needed
2. Test build locally: `docker-compose build`
3. Verify health checks still work
4. Update `docs/deployment.md`

---

## Testing Strategy

### Manual Testing Flow
1. Start services: `docker-compose up -d`
2. Check health: `curl http://localhost:8000/health`
3. Create session: `POST http://localhost:8000/api/v1/sessions` with `{"name": "test"}`
4. Get QR: `GET http://localhost:8000/api/v1/sessions/test/qr/image`
5. Scan QR with WhatsApp mobile app
6. Send test message: `POST /api/v1/messages/send/test?chat_id=...&message=Hello`

### Automated Testing (Future)
- Unit tests for controllers (mock WahaClient)
- Integration tests for routes (TestClient)
- E2E tests with real WAHA instance (Docker)

---

## Security Considerations

### Production Deployment
1. **Change default API key**: Replace `plataforma_waha_secret_key` with strong random string
2. **Use environment files**: Never commit `.env` to git
3. **Enable HTTPS**: Use reverse proxy (nginx/traefik) with SSL
4. **Rate limiting**: Add middleware to prevent abuse
5. **CORS**: Configure allowed origins in production

### Secrets Management
- Store `WAHA_API_KEY` in secure vault (AWS Secrets Manager, HashiCorp Vault)
- Use Docker secrets for sensitive data
- Rotate keys periodically

---

## Performance Optimization

### Current Optimizations
- Async HTTP client (`httpx.AsyncClient`)
- Connection pooling (reused client instance)
- Multi-stage Docker build (smaller image)
- Bytecode compilation in Docker (`UV_COMPILE_BYTECODE=1`)

### Future Improvements
- Add Redis for session caching
- Implement request queuing for rate limiting
- Use Gunicorn/Uvicorn workers for horizontal scaling

---

## Useful Resources

- **WAHA Documentation**: https://waha.devlike.pro/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **uv Documentation**: https://docs.astral.sh/uv/
- **Pydantic V2**: https://docs.pydantic.dev/latest/

---

## Agent Interaction Protocol

### When Starting a New Session
1. Read this file completely
2. Check `docs/architecture.md` for system design
3. Review recent git commits for context
4. Verify Docker services are running: `docker ps`

### When User Reports an Error
1. Ask for exact error message and logs
2. Check "Troubleshooting Guide" section above
3. Verify environment variables match expected values
4. Check WAHA logs if backend logs are unclear

### When Making Changes
1. Understand the full request before coding
2. Follow existing patterns (Controller-Router-Schema)
3. Test changes in Docker environment
4. Update relevant documentation
5. Commit with descriptive messages

---

**Last Updated**: 2026-02-10  
**Maintained By**: AI Agent (Antigravity) + Human Collaborator
