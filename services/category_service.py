import re
from datetime import datetime, timezone

from fastapi import HTTPException, status

from database import db
from security import parse_object_id

CATEGORY_COLLECTION = db["categories"]
BOOK_COLLECTION = db["books"]


def _to_public(doc: dict, book_count: int = 0) -> dict:
    return {"id": str(doc["_id"]), "name": doc["name"], "created_at": doc["created_at"], "book_count": book_count}


async def _ensure_unique(name: str, exclude_id=None) -> None:
    query = {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
    if exclude_id is not None:
        query["_id"] = {"$ne": exclude_id}
    if await CATEGORY_COLLECTION.find_one(query):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Category already exists")


async def create_category(name: str) -> dict:
    name = name.strip()
    await _ensure_unique(name)
    doc = {"name": name, "created_at": datetime.now(timezone.utc)}
    result = await CATEGORY_COLLECTION.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _to_public(doc)


async def get_all_categories() -> list[dict]:
    counts = {
        row["_id"]: row["count"]
        async for row in BOOK_COLLECTION.aggregate([{"$group": {"_id": "$category_id", "count": {"$sum": 1}}}])
    }
    return [_to_public(doc, counts.get(doc["_id"], 0)) async for doc in CATEGORY_COLLECTION.find().sort("name", 1)]


async def get_category(category_id: str) -> dict:
    oid = parse_object_id(category_id)
    doc = await CATEGORY_COLLECTION.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found")
    return _to_public(doc, await BOOK_COLLECTION.count_documents({"category_id": oid}))


async def update_category(category_id: str, name: str) -> dict:
    oid = parse_object_id(category_id)
    name = name.strip()
    await _ensure_unique(name, exclude_id=oid)
    result = await CATEGORY_COLLECTION.update_one({"_id": oid}, {"$set": {"name": name}})
    if result.matched_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found")
    return await get_category(category_id)


async def delete_category(category_id: str) -> None:
    oid = parse_object_id(category_id)
    # Refuse to orphan books: they'd disappear from listings that join on category.
    if await BOOK_COLLECTION.count_documents({"category_id": oid}, limit=1):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Category still has books; move or delete them first")
    result = await CATEGORY_COLLECTION.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found")


async def ensure_exists(category_id: str):
    oid = parse_object_id(category_id)
    if not await CATEGORY_COLLECTION.find_one({"_id": oid}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category does not exist")
    return oid
