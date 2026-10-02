from fastapi import APIRouter, Depends, status

from models.video import VideoCreateSchema, VideoResponseSchema, VideoUpdateSchema
from security import require_admin
from services import video_service

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.get("/category/{category_id}", response_model=list[VideoResponseSchema])
async def videos_by_category(category_id: str):
    return await video_service.get_videos_by_category(category_id)


@router.post(
    "/", response_model=VideoResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)]
)
async def create_video(video: VideoCreateSchema):
    return await video_service.create_video(video)


@router.put("/{video_id}", response_model=VideoResponseSchema, dependencies=[Depends(require_admin)])
async def update_video(video_id: str, changes: VideoUpdateSchema):
    return await video_service.update_video(video_id, changes)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_video(video_id: str) -> None:
    await video_service.delete_video(video_id)
