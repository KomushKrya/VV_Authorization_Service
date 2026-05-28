from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    telegram_client_id: str
    telegram_client_secret: str
    telegram_redirect_uri: str
    telegram_proxy: str = None

    service_name: str = "auth-service"
    port: int = 8000
    environment: str = "development"

    hash_salt: str

    gateway_url: str
    gateway_mock_mode: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()