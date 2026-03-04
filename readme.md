# Authorization Service

Микросервис авторизации для мобильного приложения через Telegram с использованием OpenID Connect.

## Описание

Сервис позволяет пользователям авторизоваться в мобильном приложении через свой Telegram аккаунт. 
После успешной авторизации генерируется стабильный SHA256 хэш на основе Telegram ID, который 
используется для идентификации пользователя в системе.

## Технологии

- FastAPI
- Python 3.11+
- OpenID Connect (Telegram Login)
- Pytest для тестирования
- Docker

## Установка и запуск

1. Клонировать репозиторий:
```bash
git clone https://github.com/KomushKrya/VV_Authorization_Service.git
cd vv-auth-service