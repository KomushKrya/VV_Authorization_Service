from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth
from app.config import settings
from app.core.logging_auth import setup_logging, logger

setup_logging()

app = FastAPI(
    title="Telegram Auth Service",
    description="Микросервис авторизации через Telegram",
    version="1.0.0"
)

# CORS Middleware: разрешает фронтенд-заглушке общаться с API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/routes")
async def get_routes():
    """
    Эндпоинт для API Gateway.
    Динамически собирает и возвращает список всех путей нашего микросервиса.
    """
    routes_list = []
    for route in app.routes:
        if hasattr(route, "path") and not route.path.startswith(("/openapi.json", "/docs", "/redoc")):
            routes_list.append({
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, "methods") else []
            })
    logger.info(f"Gateway requested routes. Returned {len(routes_list)} items.")
    return {"routes": routes_list}

@app.get("/")
async def root():
    return {"service": settings.service_name, "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}