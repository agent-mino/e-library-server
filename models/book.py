from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BookItem(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    publisher: str = Field(..., min_length=1)
    category_id: str
    cover_image: Optional[str] = None
    file: Optional[str] = None
    downloadable: bool = False


class UpdateBookItem(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    publisher: Optional[str] = Field(None, min_length=1)
    category_id: Optional[str] = None
    cover_image: Optional[str] = None
    file: Optional[str] = None
    downloadable: Optional[bool] = None


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    publisher: str
    category_id: str
    category_name: Optional[str] = None
    cover_image: Optional[str] = None
    file: Optional[str] = None
    downloadable: bool = False
    created_at: datetime
