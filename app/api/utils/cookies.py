from fastapi import Response

from app.core.config import settings


def set_refresh_token_cookie(
    response: Response,
    refresh_token: str
) -> None:
    """
    Refresh Token을 httpOnly cookie로 설정
    - 로그인 / refresh 시 공통 사용
    """
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,        # JS 접근 불가
        secure=not settings.DEBUG_MODE, # HTTPS에서만 전송
        samesite="lax",       # CSRF 완화
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS,
        path="/"
    )


def delete_refresh_token_cookie(response: Response) -> None:
    """
    Refresh Token 쿠키 삭제
    - 로그아웃 시 사용
    """
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=not settings.DEBUG_MODE,
        samesite="lax",
        path="/"
    )
