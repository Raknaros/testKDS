from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.services.printer import PrinterService
from app.api.websocket.connection import DashboardManager

class OrderProcessor:
    def __init__(self, db_session: AsyncSession, printer_service: PrinterService, ws_manager: DashboardManager):
        self.db_session = db_session
        self.printer = printer_service
        self.ws_manager = ws_manager

    async def create_order(self, order_data: dict):
        try:
            # 1. Crear la orden en la base de datos
            new_order = Order(
                customer_name=order_data.get("customer_name"),
                customer_phone=order_data.get("customer_phone"),
                items=order_data.get("items", []),
                total_amount=self._calculate_total(order_data.get("items", [])),
                special_instructions=order_data.get("special_instructions"),
                scheduled_time=order_data.get("scheduled_time")
            )
            
            self.db_session.add(new_order)
            await self.db_session.commit()
            await self.db_session.refresh(new_order)
            
            # 2. Imprimir ticket
            await self.printer.print_ticket(new_order)
            
            # 3. Notificar al dashboard
            await self.ws_manager.broadcast_order(new_order)
            
            return new_order
            
        except Exception as e:
            await self.db_session.rollback()
            print(f"Error processing order: {str(e)}")
            raise

    def _calculate_total(self, items: list) -> float:
        return sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
