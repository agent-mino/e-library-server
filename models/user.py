from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
# Signup schema
class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)

# Login schema
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

# Response schema
class UserResponseSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UpdateUserPassword(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

# Token schema
class TokenSchema(BaseModel):
    access_token: Optional[str] = None
    id: str
    name: str
    email : str
    token_type: str = "bearer"
