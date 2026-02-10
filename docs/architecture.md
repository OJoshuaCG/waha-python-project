# Arquitectura de WhatsPlay

## Descripción General
WhatsPlay es un wrapper de alto nivel construido con **FastAPI** para la API de WhatsApp **WAHA (WhatsApp HTTP API)**. Su objetivo es proporcionar una interfaz simplificada, tipada y segura para gestionar sesiones de WhatsApp y automatizar la mensajería.

## Flujo de Datos
1. **Cliente Externo**: Realiza peticiones a los endpoints de FastAPI (puerto 8000).
2. **FastAPI (WhatsPlay)**:
   - Valida los datos usando **Pydantic Schemas**.
   - Procesa la lógica de negocio en los **Controllers**.
   - Utiliza el **WahaClient** (Utility) para comunicarse con el servidor WAHA.
3. **WAHA Server**: Gestiona la instancia de WhatsApp Web (Chromium/Puppeteer) y realiza la comunicación real con los servidores de WhatsApp.

## Componentes Clave
- **`app/main.py`**: Punto de entrada, configuración de middleware (CORS) y registro de routers.
- **`app/controllers/`**: Contiene la lógica orquestada. Por ejemplo, el `SessionController` maneja tanto la creación como el estado de las sesiones.
- **`app/utils/waha_client.py`**: Cliente asíncrono basado en `httpx` que implementa la comunicación con el motor WAHA usando autenticación por `X-Api-Key`.
- **`app/schemas/`**: Definiciones de entrada y salida para asegurar que la API sea predecible y genere documentación Swagger correcta.

## Decisiones Técnicas
- **Inyección de Dependencias**: Se utiliza el sistema nativo de FastAPI para proveer instancias de controladores y clientes a las rutas, facilitando el testing y la modularidad.
- **Docker Multi-stage**: El Dockerfile utiliza `uv` en una etapa de construcción para generar un entorno virtual ligero que se copia a la imagen final de ejecución, minimizando el tamaño y maximizando la velocidad.
- **Seguridad Interna**: La comunicación entre WhatsPlay y WAHA está protegida por una clave API compartida definida en variables de entorno.
