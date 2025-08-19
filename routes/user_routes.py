from fastapi import APIRouter,HTTPException
from models.user import UserCreateSchema, UserLoginSchema, UserResponseSchema, TokenSchema,UpdateUser,UpdateUserPassword
from services import user_service
from typing import List

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/signup", response_model=dict)
async def signup(user_data: UserCreateSchema):
    user_id = await user_service.signup_user(user_data)
    return {"message": "User created successfully", "id": user_id}


@router.post("/login", response_model=TokenSchema)
async def login(login_data: UserLoginSchema):
    return await user_service.login_user(login_data)

@router.put("/{admin_id}", response_model=TokenSchema)
async def update_admin_route(admin_id: str, updated_admin: UpdateUser):
   return await user_service.update_admin(admin_id, updated_admin)
@router.put("/{admin_id}/password", response_model=dict)
async def update_admin_password_route(admin_id: str, password_data: UpdateUserPassword):
    success, message = await user_service.update_admin_password(
        admin_id, password_data.old_password, password_data.new_password
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}
@router.get("/", response_model=List[UserResponseSchema])
async def get_users():
    return await user_service.get_all_users()
@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(user_id: str):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

