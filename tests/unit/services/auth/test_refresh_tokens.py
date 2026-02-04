import pytest
from unittest.mock import MagicMock

from app.services.auth_service import refresh_tokens
from app.core.security import create_refresh_token


def test_refresh_tokens_성공(monkeypatch):
    user_id = "1"
    old_refresh_token, old_jti = create_refresh_token(user_id)

    monkeypatch.setattr(
        "app.services.auth_service.exists_refresh_jti",
        MagicMock(return_value=True)
    )
    monkeypatch.setattr(
        "app.services.auth_service.delete_refresh_jti",
        MagicMock()
    )
    monkeypatch.setattr(
        "app.services.auth_service.save_refresh_jti",
        MagicMock()
    )

    access_token, new_refresh_token = refresh_tokens(old_refresh_token)

    assert isinstance(access_token, str)
    assert isinstance(new_refresh_token, str)


def test_refresh_tokens_재사용_탐지_실패(monkeypatch):
    user_id = "1"
    refresh_token, jti = create_refresh_token(user_id)

    monkeypatch.setattr(
        "app.services.auth_service.exists_refresh_jti",
        MagicMock(return_value=False)
    )

    with pytest.raises(Exception) as exc:
        refresh_tokens(refresh_token)

    assert exc.value.status_code == 401

def test_refresh_tokens_유효하지_않은_토큰_실패():
    with pytest.raises(Exception) as exc:
        refresh_tokens("invalid.token.value")

    assert exc.value.status_code == 401
