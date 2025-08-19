from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt
from models.admin import AdminCreateSchema, AdminLoginSchema, TokenSchema,UpdateAdmin,UpdateAdminPassword
from database import db
from bson import ObjectId
import certifi
from pymongo import MongoClient
# MongoDB collection
ADMIN_COLLECTION = db["admin"]


client = MongoClient(
    "mongodb+srv://mazihenry2:anambra123@cluster0.s9vf5.mongodb.net",
    tlsCAFile=certifi.where()
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Config
SECRET_KEY = "SUPER_SECRET_KEY"   # 🔒 Change in production!
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


async def signup_admin(data: AdminCreateSchema) -> str:
    # Check if email already exists
    if await ADMIN_COLLECTION.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    admin_doc = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "created_at": datetime.utcnow()
    }
    result = await ADMIN_COLLECTION.insert_one(admin_doc)
    return str(result.inserted_id)


async def login_admin(data: AdminLoginSchema) -> TokenSchema:
    admin = await ADMIN_COLLECTION.find_one({"email": data.email})
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid email")
    if not verify_password(data.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "sub": str(admin["_id"]),
        "email": admin["email"]
    })

    return TokenSchema(access_token=token, id = str(admin["_id"]),name= admin["name"], email = admin["email"])

async def update_admin(admin_id: str, updated_data: UpdateAdmin):
    update_dict = {k: v for k, v in updated_data.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=404, detail="Nothing to update")
  # Nothing to update

    result = await ADMIN_COLLECTION.update_one(
        {"_id": ObjectId(admin_id)},
        {"$set": update_dict}
    )

    if result.modified_count == 0:
       raise HTTPException(status_code=200, detail="Nothing to update")


    # Fetch the updated admin
    admin = await ADMIN_COLLECTION.find_one({"_id": ObjectId(admin_id)})
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return TokenSchema(
        id=str(admin["_id"]),
        name=admin.get("name"),  # ensure it matches your schema field
        email=admin.get("email")
    )

async def update_admin_password(admin_id: str, old_password: str, new_password: str):
    admin = await ADMIN_COLLECTION.find_one({"_id": ObjectId(admin_id)})
    if not admin:
        return False, "Admin not found"

    # Verify old password
    if not pwd_context.verify(old_password, admin["password"]):
        return False, "Old password is incorrect"

    # Hash new password
    hashed_password = pwd_context.hash(new_password)

    result = await ADMIN_COLLECTION.update_one(
        {"_id": ObjectId(admin_id)},
        {"$set": {"password": hashed_password}}
    )

    if result.modified_count == 0:
        return False, "Password update failed"

    return True, "Password updated successfully"