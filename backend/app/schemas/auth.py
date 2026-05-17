from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TwoFAEnableIn(BaseModel):
    secret: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    twofa_enabled: bool
