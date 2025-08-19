from bson import ObjectId
from database import db
from models.book import BookItem, UpdateBookItem

BOOK_COLLECTION = db["books"]

# Create book

async def create_book(book: BookItem):
    book_dict = book.dict()
    # Convert string category_id to ObjectId
    book_dict["category_id"] = ObjectId(book_dict["category_id"])
    result = await BOOK_COLLECTION.insert_one(book_dict)
    return str(result.inserted_id)

# Get all books with category names
async def get_books_with_category():
    pipeline = [
        {
            "$lookup": {
                "from": "categories",
                "localField": "category_id",
                "foreignField": "_id",
                "as": "category_info"
            }
        },
        {"$unwind": "$category_info"},
        {
            "$project": {
                "title": 1,
                "author": 1,
                "publisher": 1,
                "cover_image": 1,
                "file":1,
                "downloadable": 1,
                "created_at": 1,
                "category_id": 1,
                "category_name": "$category_info.name"
            }
        }
    ]
    books = []
    cursor = BOOK_COLLECTION.aggregate(pipeline)
    async for book in cursor:
        book["_id"] = str(book["_id"])
        book["category_id"] = str(book["category_id"])
        books.append(book)
    return books

# Get single book by ID with category name
async def get_book_by_id_with_category(book_id: str):
    pipeline = [
        {"$match": {"_id": ObjectId(book_id)}},
        {
            "$lookup": {
                "from": "categories",
                "localField": "category_id",
                "foreignField": "_id",
                "as": "category_info"
            }
        },
        {"$unwind": "$category_info"},
        {
            "$project": {
                "title": 1,
                "author": 1,
                "publisher": 1,
                "cover_image": 1,
                "file":1,
                "downloadable": 1,
                "created_at": 1,
                "category_id": 1,
                "category_name": "$category_info.name"
            }
        }
    ]
    book = await BOOK_COLLECTION.aggregate(pipeline).to_list(length=1)
    if book:
        book[0]["_id"] = str(book[0]["_id"])
        book[0]["category_id"] = str(book[0]["category_id"])
        return book[0]
    return None

# Update book
async def update_book(book_id: str, updated_data: UpdateBookItem):
    update_dict = {k: v for k, v in updated_data.dict().items() if v is not None}
    if "category_id" in update_dict:
        update_dict["category_id"] = ObjectId(update_dict["category_id"])
    result = await BOOK_COLLECTION.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": update_dict}
    )
    return result.modified_count > 0
# Update only title
async def update_book_title(book_id: str, new_title: str):
    result = await BOOK_COLLECTION.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": {"title": new_title}}
    )
    return result.modified_count > 0

# Delete book
async def delete_book(book_id: str):
    result = await BOOK_COLLECTION.delete_one({"_id": ObjectId(book_id)})
    return result.deleted_count > 0
