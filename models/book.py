from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookItem(BaseModel):
    title: str
    author: str
    publisher: str
    category_id: str           # Reference to Category _id
    cover_image: Optional[str] = None
    file: Optional[str] = None
    downloadable: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UpdateBookItem(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    category_id: Optional[str] = None
    cover_image: Optional[str] = None
    file: Optional[str] = None
    downloadable: Optional[bool] = None
