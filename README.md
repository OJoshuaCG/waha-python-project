# 🚀 WhatsPlay: WAHA FastAPI Wrapper

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![WAHA](https://img.shields.io/badge/WAHA-Powered-blue?style=for-the-badge)](https://waha.devlike.pro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**WhatsPlay** es una potente interfaz backend construida con **FastAPI** diseñada para simplificar la integración con **WAHA (WhatsApp HTTP API)**. Proporciona una capa de abstracción robusta, validación de datos con Pydantic y una estructura de proyecto profesional lista para producción.

---

## ✨ Características Principales

- 🔐 **Gestión de Sesiones**: Control total sobre el ciclo de vida de tus sesiones de WhatsApp (Iniciando sesiones nuevas con un solo comando).
- 📸 **Autenticación QR**: Obtención de códigos QR en formato pairing-string o imagen Base64 para escaneo rápido.
- 💬 **Mensajería Avanzada**: Envío de mensajes de texto, respuestas (quoted messages) y gestión de chats individuales o grupales.
- 📂 **Manejo de Archivos**: Envío de imágenes, documentos y multimedia mediante rutas locales, URLs o subida directa.
- 🏥 **Health Checks Integrados**: Monitoreo automático de la salud de los servicios y del motor de WhatsApp.
- 🐋 **Docker First**: Orquestación lista para desplegar en cualquier entorno con un solo comando.

---

## 🐋 Despliegue con Docker (Recomendado)

La forma más rápida y robusta de iniciar el ecosistema completo (Backend + WAHA) es usando Docker Compose:

### 1. Iniciar Servicios
```bash
docker-compose up -d --build
```
Esto levantará:
- **WAHA Server**: El motor de WhatsApp en el puerto `3000`.
- **WhatsPlay Backend**: La API FastAPI en el puerto `8000`.

### 2. Verificar Salud
El backend esperará automáticamente a que el servidor WAHA esté saludable antes de permitir peticiones críticas.
- Backend: `http://localhost:8000/health`
- WAHA: `http://localhost:3000/ping`

---

## 🛠️ Instalación y Configuración Manual

Si prefieres ejecutarlo sin Docker (solo el backend):

### 1. Preparar Entorno
```bash
uv sync
```

### 2. Configurar Seguridad
Crea un archivo `.env` basado en el `.env.example`. Asegúrate de que la `WAHA_API_KEY` coincida con la configurada en tu servidor WAHA.
```env
WAHA_URL=http://localhost:3000
WAHA_API_KEY=tu_clave_secreta_aqui
APP_PORT=8000
APP_DEBUG=true
```

### 3. Iniciar el Servidor
```bash
uv run python -m app.main
```

---

## 📖 Documentación de la API

Explora y prueba la API interactivamente con la documentación generada automáticamente:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) (Recomendado)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Guía de Uso Rápido (Quick Start)

### Paso 1: Iniciar una Sesión
Este paso crea e inicia la sesión en WAHA.
```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
     -H "Content-Type: application/json" \
     -d '{"name": "mi_session"}'
```

### Paso 2: Escanear el QR
Obtén la imagen Base64 para escanearla con tu teléfono:
`GET http://localhost:8000/api/v1/sessions/mi_session/qr/image`

### Paso 3: Enviar un Mensaje
```python
import httpx

async def send_hello():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/messages/send/mi_session",
            params={
                "chat_id": "1234567890@c.us",
                "message": "¡Hola desde WhatsPlay!"
            }
        )
        print(response.json())
```

---

## 📂 Estructura del Proyecto

```text
backend/
├── app/
│   ├── controllers/    # Lógica de negocio avanzada y orquestación
│   ├── routes/         # Definición de endpoints API estructurados
│   ├── schemas/        # Modelos Pydantic (Validación de tipos)
│   ├── utils/          # Cliente WAHA premium e inyección de dependencias
│   └── main.py         # Punto de entrada FastAPI
├── Dockerfile          # Imagen optimizada multi-stage con uv
├── docker-compose.yml  # Orquestación de backend y motor WAHA
└── pyproject.toml      # Gestión de dependencias moderna (uv)
```

---

## 🛡️ Notas de Seguridad
El proyecto utiliza un header `X-Api-Key` para la comunicación interna entre el backend y WAHA. Por defecto, en el `docker-compose.yml` se utiliza una clave de ejemplo; asegúrate de cambiarla en entornos de producción tanto en el contenedor WAHA como en el Backend.

---
<p align="center">Hecho con ❤️ para la automatización profesional de WhatsApp</p>
