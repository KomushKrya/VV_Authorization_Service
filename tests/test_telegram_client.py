import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.telegram_client import TelegramClient

MOCK_ID_TOKEN = "mock.token.signature"
MOCK_USER_DATA = {
    "telegram_id": "123456789",
    "name": "Test User",
    "username": "testuser",
}
MOCK_JWKS = {"keys": [{"kid": "1", "kty": "RSA"}]}


@pytest.mark.asyncio
async def test_exchange_code_success():
    """Тест успешного обмена кода на токен"""
    client = TelegramClient()

    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value={"id_token": MOCK_ID_TOKEN})
        mock_response.raise_for_status = MagicMock()

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        id_token = await client.exchange_code("test_code")
        assert id_token == MOCK_ID_TOKEN


@pytest.mark.asyncio
async def test_exchange_code_missing_token():
    """Тест ошибки когда нет id_token"""
    client = TelegramClient()

    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value={"access_token": "test"})
        mock_response.raise_for_status = MagicMock()

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="No id_token"):
            await client.exchange_code("test_code")


@pytest.mark.asyncio
async def test_get_public_keys_cache():
    """Тест кэширования ключей"""
    client = TelegramClient()

    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value=MOCK_JWKS)
        mock_response.raise_for_status = MagicMock()

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        keys1 = await client.get_public_keys()
        keys2 = await client.get_public_keys()

        assert keys1 == keys2
        mock_client.return_value.__aenter__.return_value.get.assert_called_once()
