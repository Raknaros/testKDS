import aiohttp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import webhook, dashboard
from app.database.connection import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(webhook.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

async def setup_telegram_webhook():
    """Configura el webhook de Telegram automáticamente."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_WEBHOOK_URL:
        print("Telegram token or webhook URL not configured, skipping webhook setup")
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"
    data = {"url": settings.TELEGRAM_WEBHOOK_URL}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data) as response:
                result = await response.json()
                if result.get("ok"):
                    print(f"Telegram webhook configured successfully: {settings.TELEGRAM_WEBHOOK_URL}")
                else:
                    print(f"Failed to configure webhook: {result}")
        except Exception as e:
            print(f"Error configuring Telegram webhook: {e}")

@app.on_event("startup")
async def startup_event():
    await init_db()
    await setup_telegram_webhook()

@app.get("/")
async def root():
    return {"message": "Restaurant Orders API"}
