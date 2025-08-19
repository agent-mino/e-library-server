from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from database import db

# Fixed collection
CATEGORY_COLLECTION = db["categories"]

async def create_category(data: dict) -> str:
    # prevent duplicates
    existing = await CATEGORY_COLLECTION.find_one({"name": data["name"]})
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category_doc = {
        "name": data["name"],
        "created_at": datetime.utcnow()
    }
    result = await CATEGORY_COLLECTION.insert_one(category_doc)
    return str(result.inserted_id)

async def get_all_categories():
    categories = []
    async for cat in CATEGORY_COLLECTION.find():
        categories.append({
            "id": str(cat["_id"]),
            "name": cat["name"],
            "created_at": cat["created_at"]
        })
    return categories

async def update_category(category_id: str, name: str):
    result = await CATEGORY_COLLECTION.update_one(
        {"_id": ObjectId(category_id)},
        {"$set": {"name": name}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Category not found or name unchanged")
    return True

async def delete_category(category_id: str):
    result = await CATEGORY_COLLECTION.delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return True
