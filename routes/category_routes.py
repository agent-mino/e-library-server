from fastapi import APIRouter, HTTPException
from services import category_service
from models.category import CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=dict)
async def create_category(category: dict):
    category_id = await category_service.create_category(category)
    return {"message": "Category created successfully", "id": category_id}

@router.get("/", response_model=list)
async def get_categories():
    return await category_service.get_all_categories()

@router.put("/{category_id}", response_model=dict)
async def update_category(category_id: str, data: CategoryUpdate):
    updated = await category_service.update_category(category_id, data.name)
    if updated:
        return {"message": "Category updated successfully"}
    raise HTTPException(status_code=404, detail="Category not found or name unchanged")

@router.delete("/{category_id}", response_model=dict)
async def delete_category(category_id: str):
    deleted = await category_service.delete_category(category_id)
    if deleted:
        return {"message": "Category deleted successfully"}
