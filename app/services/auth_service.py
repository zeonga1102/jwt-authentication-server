from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.db.redis.refresh_token import (
    delete_all_refresh_tokens,
    delete_refresh_token,
    exists_refresh_jti,
    save_refresh_token,
)
from app.repositories.user import get_user_by_email


def login_user(db: Session, email: str, password: str) -> tuple[str, str]:
    """
    로그인
    1. 사용자 조회
    2. 비밀번호 검증
    3. access / refresh token 생성
    4. refresh token Redis에 저장
    """
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(subject=str(user.id))
    refresh_token, jti = create_refresh_token(subject=str(user.id))

    save_refresh_token(str(user.id), jti)

    return access_token, refresh_token


def refresh_tokens(refresh_token: str) -> tuple[str, str]:
    """
    Refresh Token Rotation 처리
    1. refresh token 검증
    2. Redis에서 jti 확인 (재사용 공격 감지)
    3. 기존 jti 삭제
    4. 새 access / refresh 발급
    """
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        jti = payload.get("jti")
        token_type = payload.get("type")

        if not user_id or not jti or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from None

    # 재사용 공격 감지
    if not exists_refresh_jti(jti):
        delete_all_refresh_tokens(user_id)
        raise HTTPException(status_code=401, detail="Refresh token reuse detected")

    delete_refresh_token(user_id, jti)

    # 새 토큰 발급
    new_access_token = create_access_token(subject=user_id)
    new_refresh_token, new_jti = create_refresh_token(subject=user_id)

    save_refresh_token(user_id, new_jti)

    return new_access_token, new_refresh_token
