# Solución de Problemas (Troubleshooting)

## 1. Error 401 Unauthorized
Este error ocurre cuando el Backend no se autentica correctamente con el servidor WAHA.
- **Causa**: La variable `WAHA_API_KEY` no coincide entre el servicio `backend` y el servicio `waha` en el `docker-compose.yml`.
- **Solución**: Verifica que ambas claves sean idénticas y reinicia los servicios: `docker-compose up -d`.

## 2. Error 422 Unprocessable Entity
Ocurre cuando se intenta realizar una operación inválida sobre una sesión.
- **Causa**: Intentar "iniciar" (`/start`) una sesión que aún no ha sido creada.
- **Solución**: Usa el endpoint de creación `POST /api/v1/sessions`. Este endpoint en WhatsPlay está configurado para crear e iniciar la sesión automáticamente.

## 3. El contenedor "backend" se reinicia constantemente
- **Causa**: Generalmente es un problema de permisos al intentar escribir logs.
- **Solución**: Revisa los logs (`docker logs waha-fastapi-backend`). Si ves `Permission denied: 'logs'`, asegúrate de que el Dockerfile tenga las instrucciones `RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs`.

## 4. El QR no aparece
- **Causa**: El motor WAHA tarda unos segundos en inicializar el navegador Chromium interno.
- **Solución**: Espera 10-15 segundos después de crear la sesión antes de solicitar el QR. Verifica el estado con `GET /api/v1/sessions/{name}`.

## 5. Conflicto de puertos (3000 o 8000 en uso)
- **Causa**: Instancias antiguas de WAHA o procesos Python huérfanos.
- **Solución**:
  - `docker stop $(docker ps -q)` (Cuidado: esto detiene todos los contenedores).
  - En Windows: `Stop-Process -Name python` si el proceso es local.
