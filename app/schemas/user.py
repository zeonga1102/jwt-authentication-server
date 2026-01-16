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
