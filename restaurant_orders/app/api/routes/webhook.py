from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_session
from app.services.ai_agent import AIOrderAgent
from app.services.order_processor import OrderProcessor
from app.services.printer import PrinterService
from app.api.websocket.connection import dashboard_manager
from typing import Dict, Any

router = APIRouter()
ai_agent = AIOrderAgent()
printer_service = PrinterService()

@router.post("/webhook/telegram")
async def telegram_webhook(
    update: Dict[str, Any],
    db: AsyncSession = Depends(get_session)
):
    try:
        # 1. Extraer el mensaje de Telegram
        message = update.get("message", {}).get("text", "")
        if not message:
            raise HTTPException(status_code=400, detail="No message found in update")

        # 2. Procesar el mensaje con AI
        order_data = await ai_agent.process_message(message)
        
        # 3. Procesar el pedido
        order_processor = OrderProcessor(db, printer_service, dashboard_manager)
        order = await order_processor.create_order(order_data)
        
        return {
            "status": "success",
            "order_id": order.id,
            "message": "Order processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
