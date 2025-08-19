from fastapi import APIRouter, HTTPException
from typing import List
from models.book import BookItem, UpdateBookItem
from services import book_service

router = APIRouter(prefix="/books", tags=["Books"])

# Create book
@router.post("/", response_model=dict)
async def create_book(book: BookItem):
    book_id = await book_service.create_book(book)
    return {"message": "Book created successfully", "id": book_id}

# Get all books with category names
@router.get("/", response_model=List[dict])
async def list_books():
    return await book_service.get_books_with_category()

# Get single book by ID
@router.get("/{book_id}", response_model=dict)
async def get_book(book_id: str):
    book = await book_service.get_book_by_id_with_category(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Update book (all fields)
@router.put("/{book_id}", response_model=dict)
async def update_book(book_id: str, updated_book: UpdateBookItem):
    updated = await book_service.update_book(book_id, updated_book)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book updated successfully"}

# Update only title
@router.put("/{book_id}/title", response_model=dict)
async def update_book_title(book_id: str, new_title: str):
    updated = await book_service.update_book_title(book_id, new_title)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book title updated successfully"}

# Delete book
@router.delete("/{book_id}", response_model=dict)
async def delete_book(book_id: str):
    deleted = await book_service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}
