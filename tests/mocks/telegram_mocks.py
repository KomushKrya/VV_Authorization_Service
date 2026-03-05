"""
Мок-данные для Telegram OAuth
"""

MOCK_ID_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJzdWIiOiIxMjM0NTY3ODkiLCJuYW1lIjoi0JjQstCw0L3Qn9C10YLRgNC+0LIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJpdmFucGV0cm92IiwicGljdHVyZSI6Imh0dHBzOi8vdC5tZS9pL3VzZXJwaWMvMTIzIiwicGhvbmVfbnVtYmVyIjoiKzc5MDAwMDAwMDAwIiwiaXNzIjoiaHR0cHM6Ly9vYXV0aC50ZWxlZ3JhbS5vcmciLCJhdWQiOiIxMjM0NTYiLCJleHAiOjE3MDAwMDAwMDAsImlhdCI6MTcwMDAwMDAwMH0.signature"

MOCK_USER_DATA = {
    "telegram_id": "123456789",
    "name": "ИванПетров",
    "username": "ivanpetrov",
    "photo_url": "https://t.me/i/userpic/123",
    "phone": "+79000000000",
    "all_claims": {
        "sub": "123456789",
        "name": "ИванПетров",
        "preferred_username": "ivanpetrov",
        "picture": "https://t.me/i/userpic/123",
        "phone_number": "+79000000000",
        "iss": "https://oauth.telegram.org",
        "aud": "123456"
    }
}

MOCK_JWKS = {
    "keys": [
        {
            "kid": "1",
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": "mock_modulus",
            "e": "AQAB"
        }
    ]
}

MOCK_TELEGRAM_RESPONSE = {
    "id_token": MOCK_ID_TOKEN,
    "access_token": "mock_access_token",
    "token_type": "bearer",
    "expires_in": 3600
}

MOCK_JWT_HEADER = {
    "alg": "RS256",
    "kid": "1",
    "typ": "JWT"
}