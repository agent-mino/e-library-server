from fastapi import HTTPException, status

from database import db
from security import parse_object_id
from services import accounts

USER_COLLECTION = db["users"]


async def signup_user(name: str, email: str, password: str) -> str:
    return await accounts.create_account(USER_COLLECTION, name, email, password)


async def login_user(email: str, password: str) -> dict:
    return await accounts.login(USER_COLLECTION, "user", email, password)


async def get_all_users() -> list[dict]:
    return await accounts.list_accounts(USER_COLLECTION)


async def get_user(user_id: str) -> dict:
    return await accounts.get_account(USER_COLLECTION, user_id)


async def update_user(user_id: str, changes: dict) -> dict:
    return await accounts.update_account(USER_COLLECTION, user_id, changes)


async def change_user_password(user_id: str, old: str, new: str) -> None:
    await accounts.change_password(USER_COLLECTION, user_id, old, new)


async def delete_user(user_id: str) -> None:
    result = await USER_COLLECTION.delete_one({"_id": parse_object_id(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Account not found")
