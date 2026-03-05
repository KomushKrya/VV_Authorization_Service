import pytest
from unittest.mock import AsyncMock, patch
from app.api.endpoints import auth


@pytest.mark.asyncio
async def test_login_endpoint(async_client):
    """Тест endpoint /auth/login"""
    response = await async_client.get("/auth/login")

    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "state" in data
    assert data["state"] in auth.state_storage


@pytest.mark.asyncio
async def test_callback_success(async_client, clean_state_storage):
    """Тест успешного callback"""
    login_response = await async_client.get("/auth/login")
    state = login_response.json()["state"]

    with patch('app.api.endpoints.auth.telegram_client') as mock_telegram:
        mock_telegram.exchange_code = AsyncMock(return_value="mock_token")
        mock_telegram.verify_and_decode_id_token = AsyncMock(return_value={
            "telegram_id": "123", "name": "Test User"
        })

        with patch('app.api.endpoints.auth.gateway_client') as mock_gateway:
            mock_gateway.sync_user_hash = AsyncMock(return_value=True)

            response = await async_client.get(f"/auth/callback?code=test&state={state}")

            data = response.json()
            assert data["success"] is True
            assert "user_hash" in data


@pytest.mark.asyncio
async def test_callback_invalid_state(async_client):
    """Тест невалидного state"""
    response = await async_client.get("/auth/callback?code=test&state=invalid")

    data = response.json()
    assert data["success"] is False
    assert data["error"] == "invalid_state"


@pytest.mark.asyncio
async def test_callback_missing_params(async_client):
    """Тест отсутствия параметров"""
    response = await async_client.get("/auth/callback")

    data = response.json()
    assert data["success"] is False
    assert data["error"] == "missing_params"


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """Тест health check"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"