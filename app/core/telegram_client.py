import httpx
import base64
from jose import jwt, jwk
from jose.utils import base64url_decode
from app.config import settings
from app.core.logging_auth import logger  # Добавляем импорт


class TelegramClient:
    def __init__(self):
        self.client_id = settings.telegram_client_id
        self.client_secret = settings.telegram_client_secret
        self.redirect_uri = settings.telegram_redirect_uri
        self.token_url = "https://oauth.telegram.org/token"
        self.jwks_url = "https://oauth.telegram.org/.well-known/jwks.json"

        # Кэш для публичных ключей
        self.public_keys = None
        logger.info("TelegramClient initialized")

    async def get_public_keys(self):
        """Получает публичные ключи Telegram для проверки подписи JWT"""
        if self.public_keys:
            logger.debug("Using cached public keys")
            return self.public_keys

        logger.info("Fetching public keys from Telegram")
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            self.public_keys = response.json()
            logger.info(f"Received {len(self.public_keys.get('keys', []))} public keys")
            return self.public_keys

    async def exchange_code(self, code: str):
        """
        Обменивает временный код на ID Token
        """
        logger.info("Exchanging authorization code for tokens")

        # Создаем Basic Auth заголовок
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        # Подготавливаем данные для запроса
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id
        }

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        logger.debug(f"Token request data: {data}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers=headers
            )

            logger.debug(f"Token response status: {response.status_code}")
            response.raise_for_status()
            token_data = response.json()

            # Извлекаем ID Token
            id_token = token_data.get("id_token")
            if not id_token:
                logger.error(f"No id_token in response. Got keys: {list(token_data.keys())}")
                raise ValueError(f"No id_token in response. Got: {list(token_data.keys())}")

            logger.info("Successfully obtained ID token")
            return id_token

    async def verify_and_decode_id_token(self, id_token: str):
        """
        Проверяет подпись ID Token и извлекает данные пользователя
        """
        logger.info("Verifying ID token signature")

        # Получаем заголовок токена без проверки
        unverified_header = jwt.get_unverified_header(id_token)
        logger.debug(f"Token header: {unverified_header}")

        # Получаем публичные ключи
        jwks = await self.get_public_keys()

        # Ищем ключ с нужным kid
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                public_key = key
                break

        if not public_key:
            logger.error(f"No matching public key found for kid: {unverified_header['kid']}")
            raise ValueError("No matching public key found")

        # Проверяем подпись
        message, encoded_signature = id_token.rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode())

        # Создаем ключ для проверки
        key = jwk.construct(public_key)

        if not key.verify(message.encode(), decoded_signature):
            logger.error("Invalid token signature")
            raise ValueError("Invalid signature")

        logger.info("✓ Token signature verified")

        # Декодируем payload
        claims = jwt.get_unverified_claims(id_token)

        # Проверяем обязательные поля
        if claims.get("iss") != "https://oauth.telegram.org":
            logger.error(f"Invalid issuer: {claims.get('iss')}")
            raise ValueError("Invalid issuer")

        if str(claims.get("aud")) != str(self.client_id):
            logger.error(f"Invalid audience: {claims.get('aud')}")
            raise ValueError("Invalid audience")

        logger.info(f"✓ Token claims verified for user: {claims.get('name')}")

        # Возвращаем данные пользователя
        return {
            "telegram_id": claims.get("sub") or claims.get("id"),
            "name": claims.get("name"),
            "username": claims.get("preferred_username"),
            "photo_url": claims.get("picture"),
            "phone": claims.get("phone_number"),
            "all_claims": claims
        }