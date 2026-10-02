import certifi
from motor.motor_asyncio import AsyncIOMotorClient

import settings

# Atlas (mongodb+srv) needs an explicit CA bundle on some systems; a local mongod doesn't use TLS.
_tls = {"tlsCAFile": certifi.where()} if settings.MONGO_URI.startswith("mongodb+srv://") else {}

client = AsyncIOMotorClient(settings.MONGO_URI, **_tls)
db = client[settings.DB_NAME]
