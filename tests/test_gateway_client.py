import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.core.gateway_client import GatewayClient
from app.config import settings


@pytest.mark.asyncio
async def test_mock_mode():
    """Тест mock режима"""
    original_mode = settings.gateway_mock_mode
    settings.gateway_mock_mode = True

    client = GatewayClient()
    result = await client.sync_user_hash("test_hash", "Test User")

    assert result is True
    settings.gateway_mock_mode = original_mode


@pytest.mark.asyncio
async def test_real_mode_success():
    """Тест успешной отправки"""
    original_mode = settings.gateway_mock_mode
    settings.gateway_mock_mode = False

    client = GatewayClient()

    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        result = await client.sync_user_hash("test_hash")
        assert result is True

    settings.gateway_mock_mode = original_mode


@pytest.mark.asyncio
async def test_retry_on_failure():
    """Тест повторных попыток при ошибке"""
    original_mode = settings.gateway_mock_mode
    settings.gateway_mock_mode = False

    client = GatewayClient()
    client.max_retries = 2
    client.retry_delay = 0.1

    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200

        mock_client.return_value.__aenter__.return_value.post.side_effect = [
            httpx.TimeoutException("Timeout"),
            mock_response
        ]

        result = await client.sync_user_hash("test_hash")
        assert result is True
        assert mock_client.return_value.__aenter__.return_value.post.call_count == 2

    settings.gateway_mock_mode = original_mode


@pytest.mark.asyncio
async def test_all_retries_fail():
    """Тест когда все попытки неудачны"""
    original_mode = settings.gateway_mock_mode
    settings.gateway_mock_mode = False

    client = GatewayClient()
    client.max_retries = 2
    client.retry_delay = 0.1

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.side_effect = [
            httpx.ConnectError("Connection refused"),
            httpx.ConnectError("Connection refused")
        ]

        result = await client.sync_user_hash("test_hash")
        assert result is False
        assert mock_client.return_value.__aenter__.return_value.post.call_count == 2

    settings.gateway_mock_mode = original_mode