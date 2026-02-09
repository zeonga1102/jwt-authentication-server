from unittest.mock import MagicMock
from sqlalchemy.orm import Session

import pytest
from fastapi import HTTPException

from app.services.user_service import signup_user
from app.models.user import User


def test_signup_user_성공(monkeypatch):
    db = MagicMock(spec=Session)
    mock = MagicMock()

    monkeypatch.setattr(
        "app.services.user_service.get_user_by_email",
        MagicMock(return_value=None)
    )
    monkeypatch.setattr(
        "app.services.user_service.create_user",
        mock
    )

    email = "test@example.com"
    name = "tester"

    user = signup_user(
        db=db,
        email=email,
        password="password",
        name=name
    )

    assert isinstance(user, User)
    assert user.email == email
    assert user.name == name

    mock.assert_called_once_with(db, user)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)


def test_signup_user_중복된_이메일_실패(monkeypatch):
    db = MagicMock(spec=Session)
    mock = MagicMock()
    email = "test@example.com"

    monkeypatch.setattr(
        "app.services.user_service.get_user_by_email",
        MagicMock(return_value=User(
            email=email,
            password="hashed",
            name="existing"
        ))
    )
    monkeypatch.setattr(
        "app.services.user_service.create_user",
        mock
    )

    with pytest.raises(HTTPException) as exc:
        signup_user(
            db=db,
            email=email,
            password="password",
            name="tester"
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Email already exists"

    mock.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()
