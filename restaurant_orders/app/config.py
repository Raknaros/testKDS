from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Configuración de Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/restaurant_db"
    
    # Configuración de Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""

    # Configuración de IA
    MODEL_KEY: str = ""
    MODEL: str = "openai/gpt-3.5-turbo"
    API_URL: str = "https://localhost"

    # Configuración de la impresora
    PRINTER_NAME: str = "POS-58"

    # Configuración del servidor
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Restaurant Orders System"

    # Configuración de Email para Magic Links
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
