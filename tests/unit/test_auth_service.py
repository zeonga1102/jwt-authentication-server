import pytest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.services.auth_service import login_user, refresh_tokens
from app.models.user import User
from app.core.security import create_refresh_token, hash_password


def test_login_user_성공(db: Session, monkeypatch):
    password = "password"
    email="test@example.com"
    user = User(
        email=email,
        password=hash_password(password),
        name="tester"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    monkeypatch.setattr(
        "app.services.auth_service.save_refresh_jti",
        MagicMock()
    )

    access_token, refresh_token = login_user(
        db,
        email=email,
        password=password
    )

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)


def test_login_user_존재하지_않는_이메일_실패(db: Session):
    with pytest.raises(Exception) as exc:
        login_user(
            db,
            email="nope@example.com",
            password="password"
        )

    assert exc.value.status_code == 401


def test_login_user_잘못된_비밀번호_실패(db: Session):
    email="test@example.com"
    user = User(
        email=email,
        password=hash_password("correct-password"),
        name="tester"
    )
    db.add(user)
    db.commit()

    with pytest.raises(Exception) as exc:
        login_user(
            db,
            email=email,
            password="wrong-password"
        )

    assert exc.value.status_code == 401

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
