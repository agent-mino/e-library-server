from fastapi import APIRouter, HTTPException
from models.admin import AdminCreateSchema, AdminLoginSchema, UpdateAdminPassword, TokenSchema,UpdateAdmin
from services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/signup", response_model=dict)
async def signup(admin_data: AdminCreateSchema):
    admin_id = await admin_service.signup_admin(admin_data)
    return {"message": "Admin created successfully", "id": admin_id}


@router.post("/login", response_model=TokenSchema)
async def login(login_data: AdminLoginSchema):
    return await admin_service.login_admin(login_data)

@router.put("/{admin_id}", response_model=TokenSchema)
async def update_admin_route(admin_id: str, updated_admin: UpdateAdmin):
   return await admin_service.update_admin(admin_id, updated_admin)

@router.put("/{admin_id}/password", response_model=dict)
async def update_admin_password_route(admin_id: str, password_data: UpdateAdminPassword):
    success, message = await admin_service.update_admin_password(
        admin_id, password_data.old_password, password_data.new_password
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


