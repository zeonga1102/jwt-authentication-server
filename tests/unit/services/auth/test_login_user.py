import pytest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.auth_service import login_user
from app.models.user import User
from app.core.security import hash_password


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

    mock = MagicMock()
    monkeypatch.setattr(
        "app.services.auth_service.save_refresh_token",
        mock
    )

    access_token, refresh_token = login_user(db, email, password)

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)
    mock.assert_called_once()


def test_login_user_존재하지_않는_이메일_실패(db: Session):
    with pytest.raises(HTTPException) as exc:
        login_user(db, "nope@example.com", "password")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"


def test_login_user_잘못된_비밀번호_실패(db: Session):
    email="test@example.com"
    user = User(
        email=email,
        password=hash_password("correct-password"),
        name="tester"
    )
    db.add(user)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        login_user(db, email, "wrong-password")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"