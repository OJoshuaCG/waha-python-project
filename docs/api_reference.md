# Referencia de la API

## Autenticación
Todas las peticiones internas entre WhatsPlay y WAHA utilizan el header:
- `X-Api-Key`: `{WAHA_API_KEY}`

## Endpoints Principales

### Sesiones
- `POST /api/v1/sessions`: Crea e inicia una nueva sesión.
  - Body: `{"name": "string", "config": {}}`
- `GET /api/v1/sessions/{name}`: Obtiene el estado actual de la sesión.
- `GET /api/v1/sessions/{name}/qr/image`: Devuelve el código QR en formato imagen Base64.
- `DELETE /api/v1/sessions/{name}`: Cierra la sesión y limpia los datos.

### Mensajería
- `POST /api/v1/messages/send/{session_name}`: Envía un mensaje de texto.
  - Query Params: `chat_id`, `message`.
- `GET /api/v1/messages/chats/{session_name}`: Lista todos los chats activos.

### Archivos
- `POST /api/v1/files/send/{session_name}/path`: Envía un archivo desde una ruta local del servidor.
- `POST /api/v1/files/send/{session_name}/url`: Envía un archivo descargándolo desde una URL.
- `POST /api/v1/files/send/{session_name}/upload`: Envía un archivo cargado directamente en la petición (multipart).

## Formato de Respuestas
WhatsPlay devuelve consistentemente objetos JSON. En caso de error, el formato es:
```json
{
  "error": "TipoDeError",
  "message": "Descripción amigable",
  "details": {}
}
```
