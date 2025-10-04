from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select
from sqlalchemy import update
import bcrypt
from datetime import datetime

from app.database.connection import get_session
from app.models.user import User, UserSession

router = APIRouter()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@router.post("/auth/login", response_class=HTMLResponse)
async def handle_login_form(
    username: str = Form(...),
    password: str = Form(...),
    token: str = Form(...)
):
    """Procesa los datos del formulario, valida y vincula el usuario con la sesión de Telegram."""
    try:
        # Verificar que el token de sesión existe y no ha expirado
        async for db_session in get_session():
            result = await db_session.execute(
                select(UserSession).where(
                    UserSession.token == token,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            )
            user_session = result.scalars().first()

            if not user_session:
                error_html = """
                <!DOCTYPE html><html lang="es"><head><title>Error</title><style>body{font-family: sans-serif; text-align: center; padding-top: 50px; color: #333;} h1{color: #dc3545;}</style></head>
                <body><h1>Error de autenticación</h1><p>El enlace ha expirado o es inválido. Por favor, solicita un nuevo enlace en Telegram.</p></body></html>
                """
                return HTMLResponse(content=error_html, status_code=401)

            # Buscar usuario por username
            result = await db_session.execute(select(User).where(User.username == username))
            user = result.scalars().first()

            if not user:
                error_html = """
                <!DOCTYPE html><html lang="es"><head><title>Error</title><style>body{font-family: sans-serif; text-align: center; padding-top: 50px; color: #333;} h1{color: #dc3545;}</style></head>
                <body><h1>Error de autenticación</h1><p>Usuario no encontrado. Verifica tus credenciales.</p></body></html>
                """
                return HTMLResponse(content=error_html, status_code=401)

            # Verificar contraseña
            if not verify_password(password, user.password_hash):
                error_html = """
                <!DOCTYPE html><html lang="es"><head><title>Error</title><style>body{font-family: sans-serif; text-align: center; padding-top: 50px; color: #333;} h1{color: #dc3545;}</style></head>
                <body><h1>Error de autenticación</h1><p>Contraseña incorrecta. Verifica tus credenciales.</p></body></html>
                """
                return HTMLResponse(content=error_html, status_code=401)

            # Verificar que la cuenta esté activa
            if not user.is_active:
                error_html = """
                <!DOCTYPE html><html lang="es"><head><title>Error</title><style>body{font-family: sans-serif; text-align: center; padding-top: 50px; color: #333;} h1{color: #dc3545;}</style></head>
                <body><h1>Cuenta desactivada</h1><p>Tu cuenta ha sido desactivada. Contacta al administrador.</p></body></html>
                """
                return HTMLResponse(content=error_html, status_code=401)

            # Vincular usuario con la sesión de Telegram
            await db_session.execute(
                update(UserSession)
                .where(UserSession.id == user_session.id)
                .values(user_id=user.id)
            )
            await db_session.commit()

            # Éxito - mostrar mensaje de confirmación
            success_html = """
            <!DOCTYPE html><html lang="es"><head><title>Éxito</title><style>body{font-family: sans-serif; text-align: center; padding-top: 50px; color: #333;} h1{color: #28a745;}</style></head>
            <body><h1>¡Inicio de sesión exitoso!</h1><p>Tu cuenta ha sido vinculada a tu chat de Telegram.</p><p>Ya puedes cerrar esta ventana y volver a la conversación con acceso a funciones premium.</p></body></html>
            """
            return HTMLResponse(content=success_html)

    except Exception as e:
        print(f"Login error: {e}")
        error_html = """
        <!DOCTYPE html><html lang="es"><head><title>Error</title><style>body{font-family: sans-serif; text-align: center; padding-top: 50px; color: #333;} h1{color: #dc3545;}</style></head>
        <body><h1>Error del servidor</h1><p>Ha ocurrido un error interno. Por favor, inténtalo de nuevo.</p></body></html>
        """
        return HTMLResponse(content=error_html, status_code=500)

# Only keeping the HTML form handler - other routes removed for cleanup