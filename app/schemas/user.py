from pydantic import BaseModel, ConfigDict, EmailStr


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserSignupResponse(BaseModel):
    id: int
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    로그인 요청 스키마
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    로그인 성공 응답 스키마
    """
    access_token: str
    token_type: str = "bearer"
