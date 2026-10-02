from fastapi import HTTPException, status

from database import db
from services import accounts

ADMIN_COLLECTION = db["admin"]


async def signup_admin(name: str, email: str, password: str, requester: dict | None) -> str:
    # The very first admin can sign up freely (bootstrap); after that only an admin can add admins.
    has_admins = await ADMIN_COLLECTION.count_documents({}, limit=1) > 0
    if has_admins and (requester is None or requester.get("role") != "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only an existing admin can create admins")
    return await accounts.create_account(ADMIN_COLLECTION, name, email, password)


async def login_admin(email: str, password: str) -> dict:
    return await accounts.login(ADMIN_COLLECTION, "admin", email, password)


async def get_admin(admin_id: str) -> dict:
    return await accounts.get_account(ADMIN_COLLECTION, admin_id)


async def update_admin(admin_id: str, changes: dict) -> dict:
    return await accounts.update_account(ADMIN_COLLECTION, admin_id, changes)


async def change_admin_password(admin_id: str, old: str, new: str) -> None:
    await accounts.change_password(ADMIN_COLLECTION, admin_id, old, new)
