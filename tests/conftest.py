import os

# Test settings must be in place before the app (and its settings module) is imported.
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ["DB_NAME"] = "elibrary_test"
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # One client (and event loop) for the whole session, because the Motor client binds to a loop.
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_db(client):
    from pymongo import MongoClient

    sync = MongoClient(os.environ["MONGO_URI"])
    sync.drop_database("elibrary_test")
    yield
    sync.close()


def _token(client, path, email, password, name="Test"):
    client.post(f"{path}/signup", json={"name": name, "email": email, "password": password})
    return client.post(f"{path}/login", json={"email": email, "password": password}).json()


@pytest.fixture
def admin(client):
    data = _token(client, "/admin", "admin@example.com", "admin-pass-123", "Ada Admin")
    return {"id": data["id"], "headers": {"Authorization": f"Bearer {data['access_token']}"}}


@pytest.fixture
def user(client):
    data = _token(client, "/user", "reader@example.com", "reader-pass-123", "Rita Reader")
    return {"id": data["id"], "headers": {"Authorization": f"Bearer {data['access_token']}"}}
