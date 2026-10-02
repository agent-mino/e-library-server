from fastapi import APIRouter, Depends, status

from models.category import CategoryCreate, CategoryResponse, CategoryUpdate
from security import require_admin
from services import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryResponse])
async def list_categories():
    return await category_service.get_all_categories()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    return await category_service.get_category(category_id)


@router.post(
    "/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)]
)
async def create_category(data: CategoryCreate):
    return await category_service.create_category(data.name)


@router.put("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(require_admin)])
async def update_category(category_id: str, data: CategoryUpdate):
    return await category_service.update_category(category_id, data.name)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_category(category_id: str) -> None:
    await category_service.delete_category(category_id)
