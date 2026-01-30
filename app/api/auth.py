from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.api.utils.cookies import set_refresh_token_cookie
from app.db.deps import get_db
from app.schemas.user import TokenResponse, UserLogin
from app.services.auth_service import login_user, refresh_tokens

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
