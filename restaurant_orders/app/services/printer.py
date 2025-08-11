from escpos.printer import Usb
from app.config import settings
from app.models.order import Order
from datetime import datetime

class PrinterService:
    def __init__(self):
        # Configuración de la impresora USB
        # Estos valores pueden variar según tu impresora
        self.vendor_id = 0x0456
        self.product_id = 0x0808
        
    def _connect_printer(self):
        try:
            return Usb(self.vendor_id, self.product_id)
        except Exception as e:
            print(f"Error connecting to printer: {str(e)}")
            raise

    async def print_ticket(self, order: Order):
        try:
            printer = self._connect_printer()
            
            # Formato del ticket
            printer.text("================================\n")
            printer.set(align='center', bold=True, double_height=True)
            printer.text("RESTAURANT NAME\n")
            printer.set(align='left', bold=False, double_height=False)
            printer.text("================================\n")
            
            # Información del pedido
            printer.text(f"Orden #: {order.id}\n")
            printer.text(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            printer.text(f"Cliente: {order.customer_name}\n")
            printer.text("--------------------------------\n")
            
            # Items del pedido
            printer.text("ITEMS:\n")
            for item in order.items:
                printer.text(f"{item['quantity']} x {item['name']}\n")
                printer.text(f"    ${item['price']:.2f}\n")
            
            printer.text("--------------------------------\n")
            
            # Total
            printer.set(align='right', bold=True)
            printer.text(f"TOTAL: ${order.total_amount:.2f}\n")
            printer.set(align='left', bold=False)
            
            # Instrucciones especiales
            if order.special_instructions:
                printer.text("\nInstrucciones especiales:\n")
                printer.text(f"{order.special_instructions}\n")
            
            printer.text("================================\n")
            printer.text("¡Gracias por su preferencia!\n")
            printer.cut()
            
        except Exception as e:
            print(f"Error printing ticket: {str(e)}")
            raise
        finally:
            if 'printer' in locals():
                printer.close()
