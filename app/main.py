from fastapi import FastAPI
from app.api.v1.endpoints import auth
from app.config import settings
from app.core.logging import setup_logging, logger

# Настраиваем логирование перед всем остальным
setup_logging()

app = FastAPI(
    title="Telegram Auth Service",
    description="Микросервис авторизации через Telegram",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "service": settings.service_name,
        "status": "running",
        "environment": settings.environment
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }