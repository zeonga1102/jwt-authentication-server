from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token, create_refresh_token
from app.db.redis import redis_client
from app.repositories.user import get_user_by_email
from app.core.config import settings


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

    # Refresh Token 저장
    # key: refresh:{user_id}
    redis_client.set(
        name=f"refresh:{user.id}:{jti}",
        value="valid",
        ex=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    return access_token, refresh_token
