from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)


class CategoryUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)


class CategoryResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    book_count: int = 0
