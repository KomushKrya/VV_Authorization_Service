"""
Мок-данные для Gateway
"""

MOCK_GATEWAY_RESPONSE = {
    "status": "success",
    "message": "User synced successfully"
}

MOCK_GATEWAY_ERROR = {
    "status": "error",
    "message": "User already exists"
}

MOCK_GATEWAY_RESPONSES = {
    200: {"status": "success"},
    400: {"error": "bad_request"},
    409: {"error": "conflict"},
    500: {"error": "internal_server_error"}
}