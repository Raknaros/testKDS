
import asyncio
import pytest
from unittest.mock import AsyncMock
# Añadir la raíz del proyecto al path para que Python encuentre los módulos de la app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai_agent import AIOrderAgent
from app.services.order_processor import OrderProcessor
from app.database.connection import get_session, init_db
from app.services.printer import PrinterService
from app.api.websocket.connection import DashboardManager

# --- Configuración de la Prueba ---

# Marcar todas las pruebas en este archivo para que se ejecuten con asyncio
pytestmark = pytest.mark.asyncio

# Ejemplo de pedido en lenguaje natural que usaremos para la prueba
NATURAL_LANGUAGE_ORDER = (
    "Hola, me gustaría pedir dos pizzas de pepperoni grandes a $12.50 cada una y una ensalada césar de $8. "
    "La entrega es en la Calle Falsa 123. "
    "Una de las pizzas sin aceitunas, por favor. "
    "Pagaremos con tarjeta de crédito un total de $33."
)

@pytest.fixture(scope="module")
def event_loop():
    """Crea un único event loop para todas las pruebas en este módulo."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def initialized_db():
    """Asegura que la base de datos y las tablas estén listas antes de las pruebas."""
    await init_db()

@pytest.fixture
def mock_printer_service() -> PrinterService:
    """Crea un mock para el servicio de impresión para no imprimir tickets reales."""
    mock = AsyncMock(spec=PrinterService)
    mock.print_ticket = AsyncMock()
    return mock

@pytest.fixture
def mock_ws_manager() -> DashboardManager:
    """Crea un mock para el gestor de WebSockets para no emitir eventos reales."""
    mock = AsyncMock(spec=DashboardManager)
    mock.broadcast_order = AsyncMock()
    return mock


# --- Caso de Prueba ---

async def test_full_order_processing_flow(initialized_db, mock_printer_service, mock_ws_manager):
    """
    Prueba el flujo completo: Mensaje -> LLM -> Procesador -> Base de Datos.
    
    IMPORTANTE: Esta prueba requiere una conexión real a la base de datos y que las
    funciones (insert_pedido, etc.) existan. También necesita la variable de
    entorno GOOGLE_API_KEY en el archivo .env.
    """
    print("\n--- Iniciando prueba de flujo completo de procesamiento de pedidos ---")
    
    # 1. Inicializar el agente de IA real
    print("1. Inicializando AIOrderAgent...")
    ai_agent = AIOrderAgent()
    
    # 2. Obtener una sesión de BD real y preparar el procesador de pedidos con los mocks
    print("2. Obteniendo sesión de base de datos...")
    async for db_session in get_session():
        order_processor = OrderProcessor(
            db_session=db_session,
            printer_service=mock_printer_service,
            ws_manager=mock_ws_manager
        )

        # 3. Procesar el mensaje con el LLM para obtener las llamadas a funciones
        print(f"3. Procesando mensaje con el LLM: '{NATURAL_LANGUAGE_ORDER[:60]}...'")
        function_calls = await ai_agent.process_message(NATURAL_LANGUAGE_ORDER)
        
        assert function_calls is not None, "El LLM no devolvió ninguna respuesta."
        assert len(function_calls) > 0, "El LLM no generó ninguna llamada a función."
        print(f"   -> LLM generó {len(function_calls)} llamadas a funciones.")

        # Imprimir las funciones que el LLM decidió llamar para depuración
        for part in function_calls:
            if part.function_call:
                print(f"   - LLM sugiere llamar a: {part.function_call.name} con args: {dict(part.function_call.args)}")

        # 4. Ejecutar el procesador de pedidos con las llamadas a funciones
        print("4. Ejecutando OrderProcessor para crear el pedido en la BD...")
        final_order = await order_processor.create_order_from_llm(function_calls)

        # 5. Realizar aserciones para verificar que todo funcionó
        print("5. Verificando los resultados...")
        
        assert final_order is not None, "El pedido final no debería ser nulo."
        assert "id" in final_order, "El resultado final debe contener un 'id' de pedido."
        assert "items" in final_order, "El resultado final debe contener los 'items'."
        assert final_order["id"] is not None, "El ID del pedido no puede ser nulo."
        
        print(f"   -> Pedido creado con éxito en la BD. ID: {final_order['id']}")

        # Verificar que los servicios simulados (mocks) fueron llamados
        mock_printer_service.print_ticket.assert_called_once()
        print("   -> El servicio de impresión fue invocado.")
        
        mock_ws_manager.broadcast_order.assert_called_once()
        print("   -> El gestor de WebSocket fue invocado para notificar al dashboard.")

        # Opcional: verificar que los mocks fueron llamados con los datos correctos
        mock_printer_service.print_ticket.assert_called_with(final_order)
        mock_ws_manager.broadcast_order.assert_called_with(final_order)
        
        print("\n--- Detalles del pedido final procesado: ---")
        import json
        print(json.dumps(final_order, indent=2, ensure_ascii=False))
        print("\n--- Prueba de flujo completo finalizada con éxito. ---")
