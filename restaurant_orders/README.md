# Sistema de Gestión de Pedidos para Restaurante

Este proyecto implementa un sistema integral para la gestión de pedidos de restaurante que integra múltiples tecnologías modernas para automatizar y optimizar el proceso de toma y gestión de pedidos.

## Descripción del Proyecto

### Objetivo Principal
Crear un sistema que automatice el proceso completo desde que un cliente hace un pedido vía Telegram hasta que el pedido es preparado y entregado, incluyendo la gestión en tiempo real del estado de los pedidos.

### Características Principales

1. **Bot de Telegram con IA**
    - Recepción de mensajes vía Telegram
    - Respuestas inteligentes generadas por IA (OpenRouter)
    - Comunicación bidireccional automática

2. **Procesamiento con LangChain**
    - Integración con modelos de IA via OpenRouter
    - Respuestas contextuales y naturales
    - Configuración automática del webhook

3. **API RESTful**
    - Endpoint de webhook para Telegram
    - Configuración automática al iniciar
    - Manejo de errores robusto

## Tecnologías Utilizadas

- **Backend**: FastAPI, Python
- **Base de Datos**: PostgreSQL, SQLAlchemy
- **IA/NLP**: LangChain/OpenRouter
- **Frontend**: HTML, CSS, JavaScript (WebSocket)
- **Impresión**: ESCPOS/Win32Print
- **Mensajería**: API de Telegram
- **Contenedorización**: Docker

## Alcance Actual (v1.0)

- [x] Estructura base del proyecto
- [x] Configuración inicial de la API
- [x] Integración con Telegram via webhook
- [x] Respuestas con IA via OpenRouter
- [x] Configuración automática del webhook

## Alcance Futuro (Roadmap)

- [ ] Sistema de autenticación y autorización
- [ ] Panel de administración
- [ ] Gestión de menú digital
- [ ] Sistema de pagos integrado
- [ ] Análisis de datos y reportes
- [ ] App móvil para clientes
- [ ] Sistema de fidelización
- [ ] Gestión de inventario
- [ ] Integración con sistemas contables
- [ ] Múltiples sucursales

## Próximos Pasos de Desarrollo

1. **Procesamiento de Pedidos**
    - Análisis de mensajes para extraer pedidos
    - Gestión de base de datos para órdenes
    - Sistema de impresión de tickets

2. **Dashboard en Tiempo Real**
    - Interfaz web para gestión de pedidos
    - WebSockets para actualizaciones live
    - Filtros y organización por estados

3. **Funcionalidades Avanzadas**
    - Gestión de menú
    - Sistema de pagos
    - Análisis y reportes
    - App móvil para clientes

## Requisitos de Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno (.env)
# Copiar .env.example a .env y configurar:
# - DATABASE_URL
# - TELEGRAM_BOT_TOKEN
# - MODEL_KEY (OpenRouter API key)

# 4. Iniciar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 80 --reload
```

## Estructura del Proyecto

```
restaurant_orders/
├── app/
│   ├── api/           # Endpoints y WebSockets
│   ├── core/          # Configuraciones core
│   ├── services/      # Lógica de negocio
│   ├── models/        # Modelos de datos
│   ├── database/      # Configuración DB
│   └── utils/         # Utilidades
├── frontend/          # Interface de usuario
├── tests/            # Tests unitarios
├── alembic/          # Migraciones
└── requirements.txt  # Dependencias
```

## Contribución

Por favor, lee CONTRIBUTING.md para detalles sobre nuestro código de conducta y el proceso para enviar pull requests.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE.md para más detalles.
