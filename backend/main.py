"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.api import router

app = FastAPI(title="Jobbb Finder", version="0.1.0")

# CORS: allow configured frontend URL + localhost for dev
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
_allowed_origins = [origin.strip() for origin in _frontend_url.split(",")]
if "http://localhost:5173" not in _allowed_origins:
    _allowed_origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
