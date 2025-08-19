from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategorySchema(BaseModel):
    name: str

class UpdateCategorySchema(BaseModel):
    name: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: str
class CategoryResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
