from fastapi import APIRouter, Request
import secrets
import urllib.parse
import time
import hashlib
import asyncio
from app.config import settings
from app.core.telegram_client import TelegramClient
from app.core.gateway_client import GatewayClient
from app.core.logging_auth import logger

router = APIRouter()

# Временное хранилище state
state_storage = {}

# Создаем экземпляры клиентов
telegram_client = TelegramClient()
gateway_client = GatewayClient()


@router.get("/login")
async def login():
    """
    Шаг 1: Инициируем вход через Telegram
    """
    state = secrets.token_urlsafe(32)

    state_storage[state] = {
        "created_at": time.time(),
        "used": False
    }

    logger.info(f"=== NEW LOGIN ATTEMPT ===")
    logger.info(f"Generated state: {state[:20]}...")

    params = {
        "client_id": settings.telegram_client_id,
        "redirect_uri": settings.telegram_redirect_uri,
        "response_type": "code",
        "scope": "openid profile",
        "state": state
    }

    telegram_url = f"https://oauth.telegram.org/auth?{urllib.parse.urlencode(params)}"
    logger.info(f"Telegram URL generated")
    logger.info(f"=== LOGIN ATTEMPT COMPLETE ===\n")

    return {
        "auth_url": telegram_url,
        "state": state
    }


@router.get("/callback")
async def callback(request: Request):
    """
    Шаг 2: Telegram перенаправляет пользователя сюда с кодом
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    logger.info(f"=== CALLBACK RECEIVED ===")
    logger.info(f"Code: {code[:20] if code else 'None'}...")
    logger.info(f"State: {state[:20] if state else 'None'}...")

    if not code or not state:
        logger.error("Missing code or state")
        return {
            "success": False,
            "error": "missing_params",
            "details": "Missing code or state"
        }

    # Проверяем state
    if state not in state_storage:
        logger.error(f"Invalid state: {state[:20]}... not found in storage")
        return {
            "success": False,
            "error": "invalid_state",
            "details": "State not found or expired"
        }

    state_info = state_storage[state]
    if state_info["used"]:
        logger.error(f"State already used: {state[:20]}...")
        return {
            "success": False,
            "error": "state_used",
            "details": "State already used"
        }

    logger.info(f"State validated successfully")

    # Отмечаем state как использованный
    state_storage[state]["used"] = True

    # Очищаем старые state
    current_time = time.time()
    expired_states = [s for s, info in state_storage.items()
                      if current_time - info["created_at"] > 300]
    for s in expired_states:
        logger.info(f"Cleaning up expired state: {s[:20]}...")
        del state_storage[s]

    try:
        logger.info("Exchanging code for ID token...")
        id_token = await telegram_client.exchange_code(code)
        logger.info("✓ Code exchanged successfully")

        logger.info("Verifying ID token...")
        user_data = await telegram_client.verify_and_decode_id_token(id_token)
        logger.info(f"✓ Token verified. User: {user_data.get('name')} (ID: {user_data['telegram_id']})")

        # Генерируем хэш
        telegram_id = user_data["telegram_id"]
        hash_input = f"{telegram_id}{settings.hash_salt}"
        user_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        logger.info(f"✓ Hash generated: {user_hash[:20]}...")

        logger.info("Starting Gateway sync task...")
        asyncio.create_task(
            gateway_client.sync_user_hash(user_hash, user_data.get("name"))
        )
        logger.info("Gateway sync task started")

        logger.info(f"=== AUTHENTICATION SUCCESSFUL ===\n")

        return {
            "success": True,
            "user_hash": user_hash,
            "username": user_data.get("name")
        }

    except Exception as e:
        logger.error(f"❌ Authentication error: {str(e)}")
        logger.info(f"=== AUTHENTICATION FAILED ===\n")
        return {
            "success": False,
            "error": "auth_failed",
            "details": str(e)
        }