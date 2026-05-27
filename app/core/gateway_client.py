import httpx
import asyncio
from app.core.logging_auth import logger
from app.config import settings


class GatewayClient:
    def __init__(self):
        self.gateway_url = settings.gateway_url
        self.sync_endpoint = f"{self.gateway_url}/api/v1/client/new_login"
        self.max_retries = 3
        self.retry_delay = 1
        self.mock_mode = settings.gateway_mock_mode
        logger.info(f"GatewayClient initialized. Target: {self.sync_endpoint}, Mock mode: {self.mock_mode}")

    async def sync_user_hash(self, user_hash: str, username: str = None) -> bool:
        """
        Отправляет хэш пользователя в API Gateway.
        Возвращает True в случае успеха, False при критической ошибке.
        """
        payload = {
            "username": username,
            "hash": user_hash
        }

        logger.info(f"=== GATEWAY SYNC ATTEMPT ===")
        logger.info(f"Mock mode: {self.mock_mode}")
        logger.info(f"User hash: {user_hash[:20]}...")

        if self.mock_mode:
            logger.info(f"MOCK MODE: Would send to Gateway: {payload}")
            await asyncio.sleep(0.2)  # Имитация небольшой задержки сети
            logger.info(f"✅ MOCK MODE: Successfully synced user hash\n")
            return True

        logger.info(f"Real mode: sending to {self.sync_endpoint}")

        # ИЗМЕНЕНИЕ: Создаем клиент ОДИН раз для всех попыток ретрая
        async with httpx.AsyncClient(trust_env=False) as client:
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Attempt {attempt + 1}: Sending to Gateway...")

                    response = await client.post(
                        self.sync_endpoint,
                        json=payload,
                        timeout=5.0
                    )

                    logger.info(f"Response status: {response.status_code}")

                    if response.status_code in (200, 201):
                        logger.info(f"✅ Successfully synced user hash: {user_hash[:10]}...")
                        logger.info(f"=== GATEWAY SYNC COMPLETE ===\n")
                        return True
                    else:
                        logger.warning(f"Gateway returned status {response.status_code}: {response.text}")

                except httpx.TimeoutException:
                    logger.warning(f"Attempt {attempt + 1}: Timeout connecting to Gateway")
                except httpx.ConnectError:
                    logger.warning(f"Attempt {attempt + 1}: Cannot connect to Gateway")
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1}: Unexpected error: {str(e)}")

                # Если это не последняя попытка — ждем перед повтором
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)

        logger.error(f"❌ Failed to sync after {self.max_retries} attempts")
        logger.info(f"=== GATEWAY SYNC FAILED ===\n")
        return False