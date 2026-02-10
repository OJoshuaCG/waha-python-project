# 🚀 WhatsPlay: WAHA FastAPI Wrapper

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![WAHA](https://img.shields.io/badge/WAHA-Powered-blue?style=for-the-badge)](https://waha.devlike.pro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**WhatsPlay** es una potente interfaz backend construida con **FastAPI** diseñada para simplificar la integración con **WAHA (WhatsApp HTTP API)**. Proporciona una capa de abstracción robusta, validación de datos con Pydantic y una estructura de proyecto profesional lista para producción.

---

## ✨ Características Principales

- 🔐 **Gestión de Sesiones**: Control total sobre el ciclo de vida de tus sesiones de WhatsApp (Inicio, Parada, Estado).
- 📸 **Autenticación QR**: Obtención de códigos QR en formato pairing-string o imagen Base64 de forma instantánea.
- 💬 **Mensajería Avanzada**: Envío de mensajes de texto, respuestas (quoted messages) y gestión de chats.
- 📂 **Manejo de Archivos**: Envío de imágenes, documentos y multimedia mediante rutas locales, URLs o subida directa.
- 👥 **Gestión de Grupos**: Creación de grupos y envío de mensajes masivos a comunidades.
- 🏥 **Health Checks**: Monitoreo en tiempo real de la conexión con el servidor WAHA.
- 🛠️ **Arquitectura Limpia**: Separación clara entre controladores, rutas y esquemas.

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener:

1.  **Python 3.10+** instalado.
2.  **WAHA Server** funcionando. Puedes levantarlo rápidamente con Docker:
    ```bash
    docker run -it -p 3000:3000 devlikepro/waha
    ```
3.  **uv** (El gestor de paquetes de Python ultra rápido):
    ```powershell
    # Windows (PowerShell)
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

---

## 🐋 Despliegue con Docker (Recomendado)

La forma más rápida y robusta de iniciar el ecosistema completo (Backend + WAHA) es usando Docker Compose:

### 1. Iniciar Servicios
```bash
docker-compose up -d
```
Esto levantará:
- **WAHA Server**: En el puerto `3000`.
- **WhatsPlay Backend**: En el puerto `8000`.

### 2. Verificar Salud
El backend esperará automáticamente a que el servidor WAHA esté saludable antes de iniciar.
- Backend: `curl http://localhost:8000/health`
- WAHA: `curl http://localhost:3000/ping`

---

## 🛠️ Instalación y Configuración Manual
```bash
git clone <tu-repositorio>
cd waha_project/backend
```

### 2. Sincronizar Dependencias con `uv`
```bash
uv sync
```

### 3. Configurar el Entorno
Crea un archivo `.env` basado en el ejemplo proporcionado:
```env
WAHA_URL=http://localhost:3000
APP_PORT=8000
APP_DEBUG=true
```

### 4. Iniciar el Servidor
```bash
# Modo desarrollo con auto-reload
uv run python -m app.main
```

---

## 📖 Documentación de la API

Una vez que el servidor esté corriendo, puedes explorar y probar la API interactivamente:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) (Recomendado)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Guía de Uso Rápido (Quick Start)

### Paso 1: Iniciar una Sesión
```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
     -H "Content-Type: application/json" \
     -d '{"name": "mi_session"}'
```

### Paso 2: Escanear el QR
Puedes obtener la imagen directamente para escanearla:
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
│   ├── controllers/    # Lógica de negocio avanzada
│   ├── routes/         # Definición de endpoints API
│   ├── models/         # Modelos de base de datos (si aplica)
│   ├── schemas/        # Validaciones Pydantic (Input/Output)
│   ├── utils/          # Cliente WAHA y herramientas auxiliares
│   └── main.py         # Punto de entrada de la aplicación
├── tests/              # Suite de pruebas automatizadas
├── .env.example        # Plantilla de variables de entorno
└── pyproject.toml      # Configuración de dependencias (uv)
```

---

## 🛡️ Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.

---
<p align="center">Hecho con ❤️ para la automatización de WhatsApp</p>
