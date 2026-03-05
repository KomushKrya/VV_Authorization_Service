import sys
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

@pytest_asyncio.fixture
async def async_client():
    """Асинхронный HTTP клиент"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def clean_state_storage():
    """Очищает state_storage"""
    from app.api.endpoints.auth import state_storage
    state_storage.clear()
    yield
    state_storage.clear()