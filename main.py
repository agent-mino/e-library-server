from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import settings
from database import db
from routes import admin_routes, book_routes, category_routes, user_routes, video_routes

app = FastAPI(
    title="E-Library API",
    description="REST API for an e-library: books, categories, videos, users and admin accounts.",
    version="1.1.0",
)

# Auth uses Bearer tokens (no cookies), so credentials aren't needed cross-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

for router in (
    admin_routes.router,
    user_routes.router,
    book_routes.router,
    category_routes.router,
    video_routes.router,
):
    app.include_router(router)


@app.get("/health", tags=["Health"])
async def health() -> dict:
    await db.command("ping")
    return {"status": "ok"}
