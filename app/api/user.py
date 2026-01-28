from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.deps import get_db
from app.schemas.user import TokenResponse, UserLogin, UserSignup, UserSignupResponse
from app.services.auth_service import login_user
from app.services.user_service import signup_user

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/signup", response_model=UserSignupResponse)
def signup(
    data: UserSignup,
    db: Annotated[Session, Depends(get_db)]
):
    return signup_user(db, data.email, data.password, data.name)


@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    response: Response,
    db: Annotated[Session, Depends(get_db)]
):
    access_token, refresh_token = login_user(db, data.email, data.password)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,          # JS 접근 불가
        secure=not settings.DEBUG_MODE,  # HTTPS에서만 전송
        samesite="lax",         # CSRF 완화
        max_age=60 * 60 * 24 * 7,  # 7일
        path="/"
    )

    return { "access_token": access_token }
