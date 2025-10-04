from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from telegram import Bot
import re

from app.services.ai_agent import AIOrderAgent
from app.config import settings
from app.database.connection import get_session
from app.models.user import User, MagicLink, UserSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import secrets
from datetime import datetime, timedelta

# Instancia global del agente de IA
ai_agent_instance = AIOrderAgent()

def detect_login_intent(message: str) -> bool:
    """Detect if user wants to login"""
    login_keywords = [
        'iniciar sesión', 'iniciar sesion', 'login', 'log in', 'autenticar', 'autenticarme',
        'ingresar', 'entrar', 'acceder', 'registrarme', 'registrar',
        'quiero iniciar', 'necesito iniciar', 'deseo iniciar',
        'session', 'sesion', 'loguear', 'loguearme', 'acceder',
        'enviame el enlace', 'dame el link', 'link de login', 'enlace de login'
    ]

    message_lower = message.lower()

    for keyword in login_keywords:
        if keyword in message_lower:
            return True

    return False

async def is_user_authenticated(telegram_chat_id: int) -> bool:
    """Check if a user is authenticated based on their Telegram chat ID"""
    try:
        async for db_session in get_session():
            result = await db_session.execute(
                select(UserSession).where(
                    UserSession.telegram_chat_id == telegram_chat_id,
                    UserSession.is_active == True,
                    UserSession.user_id.isnot(None),
                    UserSession.expires_at > datetime.utcnow()
                )
            )
            session = result.scalars().first()
            return session is not None
        return False
    except Exception as e:
        print(f"Error checking authentication: {e}")
        return False

async def get_user_role_by_telegram_id(telegram_chat_id: int) -> str | None:
    """Get user role by Telegram chat ID"""
    try:
        async for db_session in get_session():
            # First get the user_id from the active session
            session_result = await db_session.execute(
                select(UserSession.user_id).where(
                    UserSession.telegram_chat_id == telegram_chat_id,
                    UserSession.is_active == True,
                    UserSession.user_id.isnot(None),
                    UserSession.expires_at > datetime.utcnow()
                )
            )
            user_id = session_result.scalar()

            if user_id:
                # Then get the user role
                user_result = await db_session.execute(
                    select(User.role).where(User.id == user_id)
                )
                role = user_result.scalar()
                return role

            return None

    except Exception as e:
        print(f"Error getting user role: {e}")
        return None

async def logout_user(telegram_chat_id: int) -> bool:
    """Logout user by deactivating their session"""
    try:
        from sqlalchemy import update

        async for db_session in get_session():
            await db_session.execute(
                update(UserSession).where(
                    UserSession.telegram_chat_id == telegram_chat_id,
                    UserSession.is_active == True
                ).values(is_active=False)
            )
            await db_session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error logging out user: {e}")
        return False


# --- Router ---

router = APIRouter()

@router.post("/webhook/telegram", status_code=200)
async def telegram_webhook(update: Dict[str, Any] = Body(...)):
    """
    Endpoint para recibir actualizaciones de un webhook de Telegram y responder con IA.
    Maneja tanto pedidos como solicitudes de login.
    """
    try:
        # Extraer el mensaje de texto y chat_id del payload de Telegram
        message = update.get("message", {})
        message_text = message.get("text")
        chat_id = message.get("chat", {}).get("id")

        if not message_text or not chat_id:
            return {"status": "ok", "message": "No text message or chat_id found"}

        # Verificar si es una solicitud de login
        is_login_request = detect_login_intent(message_text)

        # Verificar comandos especiales de autenticación
        message_lower = message_text.lower()

        if is_login_request:
            # Es una solicitud de login - crear token de sesión y enviar enlace
            try:
                # Generar token de sesión único
                session_token = secrets.token_urlsafe(32)
                expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hora de validez

                # Crear sesión de usuario
                user_session = UserSession(
                    token=session_token,
                    telegram_chat_id=chat_id,
                    expires_at=expires_at
                )

                async for db_session in get_session():
                    db_session.add(user_session)
                    await db_session.commit()

                    # Crear enlace de login con token
                    login_url = f"{settings.FRONTEND_URL}/login?token={session_token}"
                    response_text = f"¡Perfecto! Para iniciar sesión, haz clic en este enlace:\n\n{login_url}\n\nIngresa tu usuario y contraseña para acceder a funciones adicionales. El enlace es válido por 1 hora."

            except Exception as db_error:
                print(f"Database error creating session: {db_error}")
                response_text = "Hubo un problema al procesar tu solicitud de inicio de sesión. Por favor, intenta de nuevo."

        elif any(keyword in message_lower for keyword in ['estoy logueado', 'estoy autenticado', 'estoy login', 'status login', 'mi estado']):
            # Verificar estado de autenticación
            if await is_user_authenticated(chat_id):
                user_role = await get_user_role_by_telegram_id(chat_id)
                response_text = f"✅ ¡Sí! Estás autenticado como **{user_role}**.\n\nPuedes acceder a funciones premium como generar contenido para redes sociales."
            else:
                response_text = "❌ No estás autenticado actualmente.\n\nEscribe 'quiero iniciar sesión' para acceder a funciones premium."

        elif any(keyword in message_lower for keyword in ['cerrar sesion', 'logout', 'cerrar sesión', 'desconectar', 'salir']):
            # Cerrar sesión
            if await logout_user(chat_id):
                response_text = "✅ Sesión cerrada exitosamente.\n\nYa no tienes acceso a funciones premium. Puedes volver a iniciar sesión cuando lo necesites."
            else:
                response_text = "❌ Hubo un problema al cerrar la sesión. Inténtalo de nuevo."

        else:
            # Es un pedido normal - procesar con IA
            ai_response = await ai_agent_instance.generate_response({"message": message_text})

            # If AI agent returns None (detected login), treat as login request
            if ai_response is None:
                login_url = f"{settings.FRONTEND_URL}/login"
                response_text = f"¡Perfecto! Para iniciar sesión, haz clic en este enlace:\n\n{login_url}\n\nIngresa tu usuario y contraseña para acceder a funciones adicionales."
            else:
                response_text = ai_response

        # Enviar respuesta al usuario vía Telegram
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=response_text)

        return {"status": "success", "response": response_text}

    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")