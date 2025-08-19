from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import List
from jose import jwt
from models.user import UserCreateSchema, UserLoginSchema, UserResponseSchema, TokenSchema,UpdateUser,UpdateUserPassword
from database import db
from bson import ObjectId
# Use the users collection from your db
USER_COLLECTION = db["users"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Config
SECRET_KEY = "SUPER_SECRET_KEY"  # 🔒 change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def signup_user(data: UserCreateSchema) -> str:
    if await USER_COLLECTION.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "created_at": datetime.utcnow()
    }
    result = await USER_COLLECTION.insert_one(user_doc)
    return str(result.inserted_id)


async def login_user(data: UserLoginSchema) -> TokenSchema:
    user = await USER_COLLECTION.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"]
    })

    return TokenSchema(access_token=token)

async def update_admin(admin_id: str, updated_data: UpdateUser):
    update_dict = {k: v for k, v in updated_data.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=404, detail="Nothing to update")
  # Nothing to update

    result = await USER_COLLECTION.update_one(
        {"_id": ObjectId(admin_id)},
        {"$set": update_dict}
    )

    if result.modified_count == 0:
       raise HTTPException(status_code=200, detail="Nothing to update")


    # Fetch the updated admin
    admin = await USER_COLLECTION.find_one({"_id": ObjectId(admin_id)})
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return TokenSchema(
        id=str(admin["_id"]),
        name=admin.get("name"),  # ensure it matches your schema field
        email=admin.get("email")
    )

async def update_admin_password(admin_id: str, old_password: str, new_password: str):
    admin = await USER_COLLECTION.find_one({"_id": ObjectId(admin_id)})
    if not admin:
        return False, "Admin not found"

    # Verify old password
    if not pwd_context.verify(old_password, admin["password"]):
        return False, "Old password is incorrect"

    # Hash new password
    hashed_password = pwd_context.hash(new_password)

    result = await USER_COLLECTION.update_one(
        {"_id": ObjectId(admin_id)},
        {"$set": {"password": hashed_password}}
    )

    if result.modified_count == 0:
        return False, "Password update failed"

    return True, "Password updated successfully"

async def get_all_users() -> List[UserResponseSchema]:
    """Fetch all users from MongoDB"""
    users_cursor = USER_COLLECTION.find()
    users = []
    async for user in users_cursor:
        users.append(UserResponseSchema(
            id=str(user["_id"]),
            name=user.get("name"),
            email=user.get("email"),
            created_at=user.get("created_at")
        ))
    return users


async def get_user_by_id(user_id: str):
    """Fetch a single user by ID from MongoDB"""
    user = await USER_COLLECTION.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    return UserResponseSchema(
        id=str(user["_id"]),
        name=user.get("name"),
        email=user.get("email"),
        created_at=user.get("created_at"),
    )