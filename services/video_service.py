from datetime import datetime, timezone

from fastapi import HTTPException, status

from database import db
from models.video import VideoCreateSchema, VideoUpdateSchema
from security import parse_object_id
from services.category_service import ensure_exists as ensure_category

VIDEO_COLLECTION = db["videos"]


def _to_public(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "description": doc.get("description"),
        "url": doc["url"],
        "category_id": str(doc["category_id"]),
        "created_at": doc["created_at"],
    }


async def create_video(video: VideoCreateSchema) -> dict:
    doc = {
        "title": video.title,
        "description": video.description,
        "url": str(video.url),
        "category_id": await ensure_category(video.category_id),
        "created_at": datetime.now(timezone.utc),
    }
    result = await VIDEO_COLLECTION.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _to_public(doc)


async def get_videos_by_category(category_id: str) -> list[dict]:
    cursor = VIDEO_COLLECTION.find({"category_id": parse_object_id(category_id)}).sort("created_at", -1)
    return [_to_public(doc) async for doc in cursor]


async def update_video(video_id: str, changes: VideoUpdateSchema) -> dict:
    oid = parse_object_id(video_id)
    update = changes.model_dump(exclude_none=True)
    if "url" in update:
        update["url"] = str(update["url"])
    if "category_id" in update:
        update["category_id"] = await ensure_category(update["category_id"])
    if update:
        result = await VIDEO_COLLECTION.update_one({"_id": oid}, {"$set": update})
        if result.matched_count == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Video not found")
    doc = await VIDEO_COLLECTION.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Video not found")
    return _to_public(doc)


async def delete_video(video_id: str) -> None:
    result = await VIDEO_COLLECTION.delete_one({"_id": parse_object_id(video_id)})
    if result.deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Video not found")
