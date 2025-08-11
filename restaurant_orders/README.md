# Sistema de Gestión de Pedidos para Restaurante

Este proyecto implementa un sistema integral para la gestión de pedidos de restaurante que integra múltiples tecnologías modernas para automatizar y optimizar el proceso de toma y gestión de pedidos.

## Descripción del Proyecto

### Objetivo Principal
Crear un sistema que automatice el proceso completo desde que un cliente hace un pedido vía Telegram hasta que el pedido es preparado y entregado, incluyendo la gestión en tiempo real del estado de los pedidos.

### Características Principales

1. **Bot de Telegram para Pedidos**
   - Recepción de pedidos a través de mensajes de texto naturales
   - Procesamiento de lenguaje natural para entender los pedidos
   - Comunicación bidireccional con el cliente

2. **Procesamiento Inteligente**
   - Integración con IA para interpretar pedidos en lenguaje natural
   - Extracción automática de:
     * Items y cantidades
     * Información del cliente
     * Instrucciones especiales
     * Horarios de entrega

3. **Gestión de Base de Datos**
   - Almacenamiento persistente de pedidos
   - Historial de clientes
   - Seguimiento de estados de pedidos
   - Reportes y análisis

4. **Sistema de Impresión**
   - Impresión automática de tickets
   - Formato personalizado para cocina
   - Gestión de cola de impresión

5. **Dashboard en Tiempo Real**
   - Visualización de pedidos activos
   - Actualización en tiempo real vía WebSocket
   - Organización por horarios y estados
   - Interfaz intuitiva para el personal

6. **API RESTful**
   - Endpoints para gestión de pedidos
   - Integración con Telegram
   - WebSockets para actualizaciones en tiempo real

## Tecnologías Utilizadas

- **Backend**: FastAPI, Python
- **Base de Datos**: PostgreSQL, SQLAlchemy
- **IA/NLP**: LangChain/Google ADK
- **Frontend**: HTML, CSS, JavaScript (WebSocket)
- **Impresión**: ESCPOS/Win32Print
- **Mensajería**: API de Telegram
- **Contenedorización**: Docker

## Alcance Actual (v1.0)

- [x] Estructura base del proyecto
- [x] Configuración inicial de la API
- [x] Modelos de base de datos básicos
- [x] Integración básica con Telegram
- [x] Dashboard simple en tiempo real

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

1. **Integración con Telegram**
   - Configuración del bot
   - Manejo de webhooks
   - Procesamiento de mensajes
   - Respuestas automáticas

2. **Procesamiento de Lenguaje Natural**
   - Configuración del agente AI
   - Entrenamiento del modelo
   - Extracción de información
   - Manejo de casos especiales

3. **Gestión de Base de Datos**
   - Migraciones
   - Modelos completos
   - Queries optimizadas
   - Backups automáticos

4. **Sistema de Impresión**
   - Configuración de impresora
   - Formatos de tickets
   - Manejo de errores
   - Cola de impresión

5. **Sistema de WebSockets**
   - Conexiones en tiempo real
   - Gestión de eventos
   - Actualización del dashboard
   - Manejo de reconexiones

6. **Frontend del Dashboard**
   - Diseño responsivo
   - Interactividad
   - Filtros y búsquedas
   - Estados y notificaciones

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
# - OPENAI_API_KEY

# 4. Iniciar el servidor
uvicorn app.main:app --reload
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
