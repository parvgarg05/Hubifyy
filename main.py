"""Hubify FastAPI application entrypoint.

This module is used by both local development and Vercel serverless runtime.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.deps import get_optional_user
from app.db import models
from app.db.database import engine, get_db
from app.routers import admin, auth, clubs, events

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

@asynccontextmanager
async def lifespan(_app: FastAPI):
  # On serverless, this can run more than once; create_all is idempotent.
  try:
    models.Base.metadata.create_all(bind=engine)
  except Exception as exc:
    print(f"Database initialization warning: {exc}")
  yield


app = FastAPI(
  title="Hubify",
  description="College Clubs & Community Hub",
  version="1.0.0",
  lifespan=lifespan,
)

if STATIC_DIR.exists():
  app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(clubs.router)
app.include_router(events.router)


@app.get("/")
async def root(
  request: Request,
  db: Session = Depends(get_db),
  user=Depends(get_optional_user),
):
  return templates.TemplateResponse(
    "index.html",
    {
      "request": request,
      "user": user,
    },
  )


@app.get("/health")
async def health() -> dict[str, str]:
  return {"status": "ok", "service": "Hubify"}