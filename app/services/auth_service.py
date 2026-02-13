from fastapi import HTTPException, logger
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.core.token_validator import decode_and_validate_token
from app.db.redis.refresh_token import (
    delete_all_refresh_tokens,
    delete_refresh_token,
    exists_refresh_jti,
    save_refresh_token,
)
from app.db.redis.blacklist import add_blacklisted_access_token
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


def logout_user(access_token: str | None, refresh_token: str | None) -> None:
    """
    완전 로그아웃
    - refresh token 삭제 (필수)
    - access token 있으면 블랙리스트 등록
    """
    # refresh 검증
    refresh_payload = decode_and_validate_token(refresh_token, "refresh")
    user_id = refresh_payload["sub"]
    jti = refresh_payload["jti"]

    delete_refresh_token(user_id, jti)

    # access 블랙리스트 등록
    if access_token:
        try:
            access_payload = decode_and_validate_token(access_token, "access")
            access_jti = access_payload["jti"]
            access_exp = access_payload["exp"]

            add_blacklisted_access_token(access_jti, access_exp)
        except HTTPException:
            # access token은 곧 만료되거나 이미 만료된 상태일 수 있으므로 검증 실패 시에도 로그아웃은 성공으로 간주
            # 다만 로그아웃 시도된 access token이 유효하지 않다는 경고 로그를 남김
            logger.warning("Invalid access token during logout")
