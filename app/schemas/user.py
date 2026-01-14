from pydantic import BaseModel, EmailStr


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserSignupResponse(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True
