from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class VideoCreateSchema(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    url: HttpUrl
    category_id: str


class VideoUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    category_id: Optional[str] = None


class VideoResponseSchema(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    url: str
    category_id: str
    created_at: datetime
