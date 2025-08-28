from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.printer import PrinterService
from app.api.websocket.connection import DashboardManager
from google.generativeai.types import Part
from typing import List
import datetime

class OrderProcessor:
    def __init__(self, db_session: AsyncSession, printer_service: PrinterService, ws_manager: DashboardManager):
        self.db_session = db_session
        self.printer = printer_service
        self.ws_manager = ws_manager

    async def create_order_from_llm(self, function_calls: List[Part]):
        pedido_id = None
        full_order_details = {}
        
        try:
            # Iniciar una transacción
            async with self.db_session.begin():
                # 1. Buscar y ejecutar insert_pedido para obtener el ID
                for part in function_calls:
                    if part.function_call.name == "insert_pedido":
                        args = part.function_call.args
                        full_order_details.update(dict(args)) # Guardar args para después
                        
                        sql = text("SELECT insert_pedido(:v_cliente_test, :v_hora_entrega, :v_destino, :v_importe_total, :v_observaciones)")
                        result = await self.db_session.execute(
                            sql,
                            {
                                "v_cliente_test": args.get("v_cliente_test"),
                                "v_hora_entrega": args.get("v_hora_entrega"),
                                "v_destino": args.get("v_destino"),
                                "v_importe_total": args.get("v_importe_total"),
                                "v_observaciones": args.get("v_observaciones")
                            }
                        )
                        pedido_id = result.scalar_one_or_none()
                        if not pedido_id:
                            raise Exception("La función insert_pedido no devolvió un ID.")
                        
                        full_order_details['id'] = pedido_id
                        full_order_details['created_at'] = datetime.datetime.utcnow().isoformat()
                        full_order_details['status'] = 'pending'
                        break
                
                if not pedido_id:
                    raise Exception("No se encontró la función 'insert_pedido' en la respuesta del LLM.")

                # 2. Ejecutar insert_detalle_pedido para cada item
                items = []
                for part in function_calls:
                    if part.function_call.name == "insert_detalle_pedido":
                        args = part.function_call.args
                        items.append(dict(args)) # Guardar para el ticket
                        
                        sql = text("SELECT insert_detalle_pedido(:v_pedido_id, :v_producto_test, :v_cantidad, :v_precio, :v_notas)")
                        await self.db_session.execute(
                            sql,
                            {
                                "v_pedido_id": pedido_id,
                                "v_producto_test": args.get("v_producto_test"),
                                "v_cantidad": args.get("v_cantidad"),
                                "v_precio": args.get("v_precio"),
                                "v_notas": args.get("v_notas")
                            }
                        )
                full_order_details['items'] = items

                # 3. Ejecutar insert_pago
                for part in function_calls:
                    if part.function_call.name == "insert_pago":
                        args = part.function_call.args
                        sql = text("SELECT insert_pago(:v_pedido_id, :v_metodo, :v_importe, :v_estado, :v_fecha_hora)")
                        await self.db_session.execute(
                            sql,
                            {
                                "v_pedido_id": pedido_id,
                                "v_metodo": args.get("v_metodo"),
                                "v_importe": args.get("v_importe"),
                                "v_estado": args.get("v_estado"),
                                "v_fecha_hora": args.get("v_fecha_hora")
                            }
                        )
                        break
            
            # La transacción se confirma aquí automáticamente con 'async with'
            
            # 4. Imprimir ticket y notificar al dashboard
            # Usamos el diccionario que hemos construido
            await self.printer.print_ticket(full_order_details)
            await self.ws_manager.broadcast_order(full_order_details)
            
            return full_order_details

        except Exception as e:
            # El rollback es automático si 'async with' falla
            print(f"Error processing order: {str(e)}")
            raise
