from jose import JWTError, jwt
from fastapi import HTTPException

from app.core.config import settings


def decode_and_validate_token(token: str, expected_type: str) -> dict:
    """
    JWT를 decode하고 유효성 검증
    - type 검증
    - 필수 필드 검증
    실패 시 예외 발생
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(status_code=401, detail=f"Invalid {expected_type} token") from None

    token_type = payload.get("type")
    user_id = payload.get("sub")
    jti = payload.get("jti")

    if token_type != expected_type or not user_id or not jti:
        raise HTTPException(status_code=401, detail=f"Invalid {expected_type} token")

    return payload
