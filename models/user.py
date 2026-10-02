from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from models.admin import TokenSchema  # same token shape for users and admins

__all__ = [
    "UserCreateSchema",
    "UserLoginSchema",
    "UserResponseSchema",
    "UpdateUser",
    "UpdateUserPassword",
    "TokenSchema",
]


class UserCreateSchema(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime


class UpdateUser(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None


class UpdateUserPassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
