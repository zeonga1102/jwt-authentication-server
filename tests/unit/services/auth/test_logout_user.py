from unittest.mock import MagicMock
from fastapi import HTTPException

from app.services.auth_service import logout_user


def test_logout_user_성공(monkeypatch):
    user_id = "1"
    refresh_jti = "refresh-jti"
    access_jti = "access-jti"

    refresh_payload = {"sub": user_id, "jti": refresh_jti}
    access_payload = {"sub": user_id, "jti": access_jti, "exp": 9999999999}

    monkeypatch.setattr(
        "app.services.auth_service.decode_and_validate_token",
        MagicMock(side_effect=[refresh_payload, access_payload])
    )
    delete_mock = MagicMock()
    blacklist_mock = MagicMock()

    monkeypatch.setattr(
        "app.services.auth_service.delete_refresh_token",
        delete_mock
    )
    monkeypatch.setattr(
        "app.services.auth_service.add_blacklisted_access_token",
        blacklist_mock
    )

    logout_user("access.token", "refresh.token")

    delete_mock.assert_called_once_with(user_id, refresh_jti)
    blacklist_mock.assert_called_once_with(access_jti, 9999999999)


def test_logout_user_access_token_없음_성공(monkeypatch):
    user_id = "1"
    refresh_jti = "refresh-jti"

    refresh_payload = {"sub": user_id, "jti": refresh_jti}

    monkeypatch.setattr(
        "app.services.auth_service.decode_and_validate_token",
        MagicMock(return_value=refresh_payload)
    )

    delete_mock = MagicMock()
    blacklist_mock = MagicMock()
    monkeypatch.setattr(
        "app.services.auth_service.delete_refresh_token",
        delete_mock
    )
    monkeypatch.setattr(
        "app.services.auth_service.add_blacklisted_access_token",
        blacklist_mock
    )

    logout_user(None, "refresh.token")

    delete_mock.assert_called_once_with(user_id, refresh_jti)
    blacklist_mock.assert_not_called()


def test_logout_user_유효하지_않은_access_token_성공(monkeypatch):
    user_id = "1"
    refresh_jti = "refresh-jti"

    refresh_payload = {"sub": user_id, "jti": refresh_jti}

    def side_effect(token, expected_type):
        if expected_type == "refresh":
            return refresh_payload
        raise HTTPException(status_code=401)

    monkeypatch.setattr(
        "app.services.auth_service.decode_and_validate_token",
        side_effect
    )

    delete_mock = MagicMock()
    blacklist_mock = MagicMock()

    monkeypatch.setattr(
        "app.services.auth_service.delete_refresh_token",
        delete_mock
    )
    monkeypatch.setattr(
        "app.services.auth_service.add_blacklisted_access_token",
        blacklist_mock
    )

    logout_user("invalid.access", "refresh.token")

    delete_mock.assert_called_once_with(user_id, refresh_jti)
    blacklist_mock.assert_not_called()
