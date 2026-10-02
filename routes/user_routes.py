from fastapi import APIRouter, Depends, status

from models.user import (
    TokenSchema,
    UpdateUser,
    UpdateUserPassword,
    UserCreateSchema,
    UserLoginSchema,
    UserResponseSchema,
)
from security import current_principal, require_admin, require_self
from services import user_service

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(data: UserCreateSchema) -> dict:
    user_id = await user_service.signup_user(data.name, data.email, data.password)
    return {"message": "User created successfully", "id": user_id}


@router.post("/login", response_model=TokenSchema)
async def login(data: UserLoginSchema):
    return await user_service.login_user(data.email, data.password)


@router.get("/", response_model=list[UserResponseSchema], dependencies=[Depends(require_admin)])
async def list_users():
    return await user_service.get_all_users()


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(user_id: str, principal: dict = Depends(current_principal)):
    if principal.get("role") != "admin":
        require_self(principal, user_id, "user")
    return await user_service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponseSchema)
async def update_user(user_id: str, changes: UpdateUser, principal: dict = Depends(current_principal)):
    require_self(principal, user_id, "user")
    return await user_service.update_user(user_id, changes.model_dump())


@router.put("/{user_id}/password")
async def change_password(user_id: str, data: UpdateUserPassword, principal: dict = Depends(current_principal)) -> dict:
    require_self(principal, user_id, "user")
    await user_service.change_user_password(user_id, data.old_password, data.new_password)
    return {"message": "Password updated successfully"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_user(user_id: str) -> None:
    await user_service.delete_user(user_id)
