import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError
from app.config import Settings

def test_settings_default_values():
    """Тест значений по умолчанию"""
    with patch.dict(os.environ, {
        "telegram_client_id": "test_id",
        "telegram_client_secret": "test_secret",
        "telegram_redirect_uri": "http://test/callback",
        "hash_salt": "test_salt",
        "gateway_url": "http://gateway:8080"
    }, clear=True):
        settings = Settings()
        assert settings.service_name == "auth-service"
        assert settings.port == 8000
        assert settings.gateway_mock_mode is True

def test_settings_custom_values():
    """Тест кастомных значений"""
    with patch.dict(os.environ, {
        "telegram_client_id": "custom_id",
        "telegram_client_secret": "custom_secret",
        "telegram_redirect_uri": "https://custom/callback",
        "hash_salt": "custom_salt",
        "gateway_url": "https://gateway.custom",
        "gateway_mock_mode": "false",
        "port": "9000",
        "environment": "production"
    }, clear=True):
        settings = Settings()
        assert settings.telegram_client_id == "custom_id"
        assert settings.gateway_mock_mode is False
        assert settings.port == 9000
        assert settings.environment == "production"
