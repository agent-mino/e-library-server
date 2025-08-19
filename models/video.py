from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VideoCreateSchema(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    category_id: str

class VideoResponseSchema(VideoCreateSchema):
    id: str
    created_at: datetime
