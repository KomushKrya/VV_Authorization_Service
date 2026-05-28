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
    Динамически собирает список путей в новом плоском формате:
    каждому HTTP-методу соответствует отдельный объект.
    """
    routes_list = []
    for route in app.routes:
        # Исключаем служебные эндпоинты документации FastAPI
        if hasattr(route, "path") and not route.path.startswith(("/openapi.json", "/docs", "/redoc")):
            # Во FastAPI у одного пути может быть сет из нескольких методов, например {"GET", "POST"}
            # Для нового формата Шлюза мы разворачиваем их в отдельные элементы
            methods = route.methods if hasattr(route, "methods") else ["GET"]
            for method in methods:
                routes_list.append({
                    "method": method.upper(),
                    "path": route.path
                })

    logger.info(f"Gateway requested routes in new format. Returned {len(routes_list)} items.")
    return {"routes": routes_list}

@app.get("/")
async def root():
    return {"service": settings.service_name, "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}