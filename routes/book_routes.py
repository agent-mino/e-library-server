from fastapi import APIRouter, Depends, status

from models.book import BookItem, BookResponse, UpdateBookItem
from security import require_admin
from services import book_service

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[BookResponse])
async def list_books(category_id: str | None = None, q: str | None = None):
    return await book_service.list_books(category_id, q)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str):
    return await book_service.get_book(book_id)


@router.post(
    "/", response_model=BookResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)]
)
async def create_book(book: BookItem):
    return await book_service.create_book(book)


@router.put("/{book_id}", response_model=BookResponse, dependencies=[Depends(require_admin)])
async def update_book(book_id: str, changes: UpdateBookItem):
    return await book_service.update_book(book_id, changes)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_book(book_id: str) -> None:
    await book_service.delete_book(book_id)
