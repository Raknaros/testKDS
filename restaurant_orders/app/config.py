from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Configuración de Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/restaurant_db"
    
    # Configuración de Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    
    # Configuración de la impresora
    PRINTER_NAME: str = "POS-58"
    
    # Configuración del servidor
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Restaurant Orders System"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
