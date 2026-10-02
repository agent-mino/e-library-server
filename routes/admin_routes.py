from fastapi import APIRouter, Depends, status

from models.admin import (
    AdminCreateSchema,
    AdminLoginSchema,
    AdminResponseSchema,
    TokenSchema,
    UpdateAdmin,
    UpdateAdminPassword,
)
from security import optional_principal, require_admin, require_self
from services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(data: AdminCreateSchema, requester: dict | None = Depends(optional_principal)) -> dict:
    admin_id = await admin_service.signup_admin(data.name, data.email, data.password, requester)
    return {"message": "Admin created successfully", "id": admin_id}


@router.post("/login", response_model=TokenSchema)
async def login(data: AdminLoginSchema):
    return await admin_service.login_admin(data.email, data.password)


@router.get("/me", response_model=AdminResponseSchema)
async def me(principal: dict = Depends(require_admin)):
    return await admin_service.get_admin(principal["sub"])


@router.put("/{admin_id}", response_model=AdminResponseSchema)
async def update_admin(admin_id: str, changes: UpdateAdmin, principal: dict = Depends(require_admin)):
    require_self(principal, admin_id, "admin")
    return await admin_service.update_admin(admin_id, changes.model_dump())


@router.put("/{admin_id}/password")
async def change_password(admin_id: str, data: UpdateAdminPassword, principal: dict = Depends(require_admin)) -> dict:
    require_self(principal, admin_id, "admin")
    await admin_service.change_admin_password(admin_id, data.old_password, data.new_password)
    return {"message": "Password updated successfully"}
