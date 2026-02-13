from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.api.utils.cookies import delete_refresh_token_cookie, set_refresh_token_cookie
from app.db.deps import get_db
from app.schemas.user import TokenResponse, UserLogin
from app.services.auth_service import login_user, refresh_tokens, logout_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    response: Response,
    db: Annotated[Session, Depends(get_db)]
):
    access_token, refresh_token = login_user(db, data.email, data.password)

    set_refresh_token_cookie(response, refresh_token)

    return { "access_token": access_token }


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response
):
    """
    Refresh Token을 이용해 Access Token 재발급
    - Refresh Token은 httpOnly cookie에서 읽음
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    access_token, new_refresh_token = refresh_tokens(refresh_token)

    set_refresh_token_cookie(response, new_refresh_token)

    return TokenResponse(access_token=access_token)


@router.post("/logout")
def logout(
    request: Request,
    response: Response
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    auth_header = request.headers.get("Authorization")
    access_token = None
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.replace("Bearer ", "")

    logout_user(access_token, refresh_token)

    delete_refresh_token_cookie(response)

    return { "message": "Logged out successfully" }
