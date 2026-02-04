from fastapi import Response
from unittest.mock import MagicMock

from app.api.utils.cookies import set_refresh_token_cookie
from app.core.config import settings

def test_set_refresh_token_cookie():
    response = Response()
    response.set_cookie = MagicMock()

    refresh_token = "refresh-token-value"

    set_refresh_token_cookie(response, refresh_token)

    response.set_cookie.assert_called_once_with(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG_MODE,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS,
        path="/"
    )
