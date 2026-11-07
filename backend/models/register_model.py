from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict
)

from typing import Literal, Optional


class RegisterRequest(BaseModel):

    username: str = Field(
        min_length=2,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )

    confirm_password: str = Field(
        min_length=6,
        max_length=100
    )

    role: Literal["user", "admin"]


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class UpdateUserRequest(BaseModel):

    username: str = Field(
        min_length=2,
        max_length=50
    )

    email: EmailStr

    role: Literal["user", "admin"]

    password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=100
    )


class PublicUser(BaseModel):

    model_config = ConfigDict(
        extra="ignore"
    )

    id: str
    username: str
    email: EmailStr
    role: str
    created_at: str