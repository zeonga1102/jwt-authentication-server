import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.services.auth_service import refresh_tokens
from app.core.security import create_refresh_token, create_access_token


def test_refresh_tokens_성공(monkeypatch):
    user_id = "1"
    old_refresh_token, old_jti = create_refresh_token(user_id)

    exists_mock = MagicMock(return_value=True)
    delete_mock = MagicMock()
    save_mock = MagicMock()

    monkeypatch.setattr(
        "app.services.auth_service.exists_refresh_jti",
        exists_mock
    )
    monkeypatch.setattr(
        "app.services.auth_service.delete_refresh_token",
        delete_mock
    )
    monkeypatch.setattr(
        "app.services.auth_service.save_refresh_token",
        save_mock
    )

    access_token, new_refresh_token = refresh_tokens(old_refresh_token)

    assert isinstance(access_token, str)
    assert isinstance(new_refresh_token, str)

    exists_mock.assert_called_once_with(old_jti)
    delete_mock.assert_called_once_with(user_id, old_jti)
    save_mock.assert_called_once()


def test_refresh_tokens_재사용_탐지_실패(monkeypatch):
    user_id = "1"
    refresh_token, _ = create_refresh_token(user_id)

    delete_all_mock = MagicMock()
    save_mock = MagicMock()

    monkeypatch.setattr(
        "app.services.auth_service.exists_refresh_jti",
        MagicMock(return_value=False)
    )
    monkeypatch.setattr(
        "app.services.auth_service.delete_all_refresh_tokens",
        delete_all_mock
    )
    monkeypatch.setattr(
        "app.services.auth_service.save_refresh_token",
        save_mock
    )

    with pytest.raises(HTTPException) as exc:
        refresh_tokens(refresh_token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Refresh token reuse detected"

    delete_all_mock.assert_called_once_with(user_id)
    save_mock.assert_not_called()


def test_refresh_tokens_유효하지_않은_토큰_실패():
    with pytest.raises(HTTPException) as exc:
        refresh_tokens("invalid.token.value")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid refresh token"
