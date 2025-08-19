from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Input model for signup
class AdminCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)

# Input model for login
class AdminLoginSchema(BaseModel):
    email: EmailStr
    password: str

# Output model for responses
class AdminResponseSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class TokenSchema(BaseModel):
    access_token: Optional[str] = None
    id: str
    name: str
    email : str

class UpdateAdmin(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UpdateAdminPassword(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)