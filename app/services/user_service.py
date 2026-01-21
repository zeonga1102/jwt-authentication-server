from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import create_user, get_user_by_email


def signup_user(
    db: Session,
    email: str,
    password: str,
    name: str
) -> User:
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=email,
        password=hash_password(password),
        name=name
    )

    create_user(db, user)
    db.commit()
    db.refresh(user)

    return user
