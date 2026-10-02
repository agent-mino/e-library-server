"""Account logic shared by admins and users; they differ only in collection and role."""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from security import create_access_token, hash_password, parse_object_id, verify_password


def to_public(doc: dict) -> dict:
    return {"id": str(doc["_id"]), "name": doc["name"], "email": doc["email"], "created_at": doc["created_at"]}


async def create_account(collection: AsyncIOMotorCollection, name: str, email: str, password: str) -> str:
    if await collection.find_one({"email": email}):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    result = await collection.insert_one(
        {
            "name": name,
            "email": email,
            "password": hash_password(password),
            "created_at": datetime.now(timezone.utc),
        }
    )
    return str(result.inserted_id)


async def login(collection: AsyncIOMotorCollection, role: str, email: str, password: str) -> dict:
    account = await collection.find_one({"email": email})
    # Same message for unknown email and wrong password, so emails can't be enumerated.
    if not account or not verify_password(password, account["password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    account_id = str(account["_id"])
    return {
        "access_token": create_access_token(account_id, role, account["email"]),
        "id": account_id,
        "name": account["name"],
        "email": account["email"],
    }


async def get_account(collection: AsyncIOMotorCollection, account_id: str) -> dict:
    account = await collection.find_one({"_id": parse_object_id(account_id)})
    if not account:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Account not found")
    return to_public(account)


async def list_accounts(collection: AsyncIOMotorCollection) -> list[dict]:
    return [to_public(doc) async for doc in collection.find().sort("created_at", -1)]


async def update_account(collection: AsyncIOMotorCollection, account_id: str, changes: dict) -> dict:
    oid = parse_object_id(account_id)
    changes = {k: v for k, v in changes.items() if v is not None}
    if "email" in changes and await collection.find_one({"email": changes["email"], "_id": {"$ne": oid}}):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    if changes:
        result = await collection.update_one({"_id": oid}, {"$set": changes})
        if result.matched_count == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Account not found")
    return await get_account(collection, account_id)


async def change_password(collection: AsyncIOMotorCollection, account_id: str, old: str, new: str) -> None:
    oid = parse_object_id(account_id)
    account = await collection.find_one({"_id": oid})
    if not account:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Account not found")
    if not verify_password(old, account["password"]):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    await collection.update_one({"_id": oid}, {"$set": {"password": hash_password(new)}})
