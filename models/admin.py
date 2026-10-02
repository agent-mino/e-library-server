from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class AdminCreateSchema(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)


class AdminLoginSchema(BaseModel):
    email: EmailStr
    password: str


class AdminResponseSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: str
    name: str
    email: str


class UpdateAdmin(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None


class UpdateAdminPassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
