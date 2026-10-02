"""Password hashing, JWT issuing and the auth dependencies used by the routes."""

from datetime import datetime, timedelta, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str, email: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    claims = {"sub": subject, "role": role, "email": email, "exp": expires}
    return jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def _decode(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise _unauthorized("Not authenticated")
    try:
        return jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise _unauthorized("Invalid or expired token") from None


async def current_principal(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    """Any signed-in user or admin. Returns the token claims."""
    return _decode(credentials)


async def optional_principal(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict | None:
    return _decode(credentials) if credentials else None


async def require_admin(principal: dict = Depends(current_principal)) -> dict:
    if principal.get("role") != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return principal


def require_self(principal: dict, account_id: str, role: str) -> None:
    """Only the account owner may change their own profile or password."""
    if principal.get("role") != role or principal.get("sub") != account_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can only modify your own account")


def parse_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid id") from None
