from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.user import UserSignup, UserSignupResponse
from app.services.user_service import signup_user

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/signup", response_model=UserSignupResponse)
def signup(
    data: UserSignup,
    db: Annotated[Session, Depends(get_db)]
):
    return signup_user(db, data.email, data.password, data.name)
