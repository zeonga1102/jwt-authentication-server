from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.user_service import signup_user
from app.models.user import User


def test_signup_user_성공():
    db = MagicMock(spec=Session)

    # email 중복 없음
    db.query.return_value.filter.return_value.first.return_value = None

    user = signup_user(
        db=db,
        email="test@example.com",
        password="password",
        name="tester"
    )

    assert isinstance(user, User)
    assert user.email == "test@example.com"
    assert user.name == "tester"

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


def test_signup_user_중복된_이메일_실패():
    db = MagicMock(spec=Session)

    # email 중복
    db.query.return_value.filter.return_value.first.return_value = User(
        email="test@example.com",
        password="hashed",
        name="existing"
    )

    with pytest.raises(HTTPException) as exc:
        signup_user(
            db=db,
            email="test@example.com",
            password="password",
            name="tester"
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Email already exists"
