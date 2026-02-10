# Guía de Despliegue

## Docker Compose (Recomendado)
Es la forma más sencilla de desplegar WhatsPlay junto con el motor WAHA.

### Requisitos
- Docker y Docker Compose instalado.
- Puertos 8000 (Backend) y 3000 (WAHA) disponibles.

### Pasos
1. Ejecutar `docker-compose up -d --build`.
2. Verificar logs: `docker-compose logs -f backend`.

---

## Despliegue Manual (Solo Backend)

### Requisitos
- Python 3.10+
- Instalador `uv`

### Configuración
1. Clonar repositorio.
2. Ejecutar `uv sync`.
3. Crear archivo `.env` (copiar de `.env.example`).
4. Configurar `WAHA_URL` apuntando a tu instancia de WAHA (ej: `http://localhost:3000`).

### Ejecución
```bash
uv run python -m app.main
```

## Variables de Entorno Clave
| Variable | Descripción | Valor Docker | Valor Local |
|----------|-------------|--------------|-------------|
| `WAHA_URL` | URL del motor WAHA | `http://waha:3000` | `http://localhost:3000` |
| `WAHA_API_KEY` | Clave de seguridad | Requerido | Requerido |
| `APP_DEBUG` | Modo desarrollo | `true`/`false` | `true`/`false` |
| `UPLOAD_DIR` | Directorio de archivos | `/app/uploads` | `./uploads` |
