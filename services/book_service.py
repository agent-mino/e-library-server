import re
from datetime import datetime, timezone

from fastapi import HTTPException, status

from database import db
from models.book import BookItem, UpdateBookItem
from security import parse_object_id
from services.category_service import ensure_exists as ensure_category

BOOK_COLLECTION = db["books"]

# Join each book with its category name. Books keep showing even if the category lookup fails.
_WITH_CATEGORY = [
    {"$lookup": {"from": "categories", "localField": "category_id", "foreignField": "_id", "as": "category"}},
    {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}},
    {"$addFields": {"category_name": "$category.name"}},
    {"$project": {"category": 0}},
]


def _to_public(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "author": doc["author"],
        "publisher": doc["publisher"],
        "category_id": str(doc["category_id"]),
        "category_name": doc.get("category_name"),
        "cover_image": doc.get("cover_image"),
        "file": doc.get("file"),
        "downloadable": doc.get("downloadable", False),
        "created_at": doc["created_at"],
    }


async def create_book(book: BookItem) -> dict:
    doc = book.model_dump()
    doc["category_id"] = await ensure_category(book.category_id)
    doc["created_at"] = datetime.now(timezone.utc)
    result = await BOOK_COLLECTION.insert_one(doc)
    return await get_book(str(result.inserted_id))


async def list_books(category_id: str | None = None, search: str | None = None) -> list[dict]:
    match: dict = {}
    if category_id:
        match["category_id"] = parse_object_id(category_id)
    if search:
        pattern = {"$regex": re.escape(search), "$options": "i"}  # literal match, not user-supplied regex
        match["$or"] = [{"title": pattern}, {"author": pattern}]
    pipeline = ([{"$match": match}] if match else []) + [{"$sort": {"created_at": -1}}] + _WITH_CATEGORY
    return [_to_public(doc) async for doc in BOOK_COLLECTION.aggregate(pipeline)]


async def get_book(book_id: str) -> dict:
    pipeline = [{"$match": {"_id": parse_object_id(book_id)}}] + _WITH_CATEGORY
    docs = await BOOK_COLLECTION.aggregate(pipeline).to_list(length=1)
    if not docs:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    return _to_public(docs[0])


async def update_book(book_id: str, changes: UpdateBookItem) -> dict:
    oid = parse_object_id(book_id)
    update = changes.model_dump(exclude_none=True)
    if "category_id" in update:
        update["category_id"] = await ensure_category(update["category_id"])
    if update:
        result = await BOOK_COLLECTION.update_one({"_id": oid}, {"$set": update})
        if result.matched_count == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    return await get_book(book_id)


async def delete_book(book_id: str) -> None:
    result = await BOOK_COLLECTION.delete_one({"_id": parse_object_id(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
