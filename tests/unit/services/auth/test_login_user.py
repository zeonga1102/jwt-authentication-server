import pytest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

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
