from datetime import datetime

from jose import jwt

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token

def test_hash_and_verify_password():
    password = "plain-password"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True


def test_verify_password_fail():
    password = "correct-password"
    wrong_password = "wrong-password"

    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_create_access_token():
    user_id = "1"

    token = create_access_token(user_id)

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert "exp" in payload

    exp = datetime.fromtimestamp(payload["exp"])
    now = datetime.now()

    assert exp > now


def test_create_refresh_token():
    user_id = "1"

    token, jti = create_refresh_token(user_id)

    assert isinstance(jti, str)
    assert len(jti) > 0

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti
    assert "exp" in payload
