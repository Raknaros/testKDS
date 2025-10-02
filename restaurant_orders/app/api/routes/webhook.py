from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from telegram import Bot

from app.services.ai_agent import AIOrderAgent
from app.config import settings

# Instancia global del agente de IA
ai_agent_instance = AIOrderAgent()


# --- Router ---

router = APIRouter()

@router.post("/webhook/telegram", status_code=200)
async def telegram_webhook(update: Dict[str, Any] = Body(...)):
    """
    Endpoint para recibir actualizaciones de un webhook de Telegram y responder con IA.
    """
    try:
        # Extraer el mensaje de texto y chat_id del payload de Telegram
        message = update.get("message", {})
        message_text = message.get("text")
        chat_id = message.get("chat", {}).get("id")

        if not message_text or not chat_id:
            return {"status": "ok", "message": "No text message or chat_id found"}

        # Generar respuesta con el modelo de IA
        response_text = await ai_agent_instance.generate_response({"message": message_text})

        # Enviar respuesta al usuario vía Telegram
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=response_text)

        return {"status": "success", "response": response_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")