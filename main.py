"""
Hubify - College Clubs & Community Hub
FastAPI Application Entry Point

Works both locally and on Vercel serverless.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import auth, admin, events
from app.core.deps import get_optional_user
from app.db.database import get_db 
from sqlalchemy.orm import Session 
from fastapi import Depends
from app.db import models
from app.db.database import engine

# Determine base directory (works on both local and Vercel)
BASE_DIR = Path(__file__).resolve().parent

# Create FastAPI application
app = FastAPI(
    title="Hubify",
    description="College Clubs & Community Hub",
    version="1.0.0"
)

# Setup static files with proper path handling for Vercel
static_dir = BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Setup templates with proper path handling for Vercel
templates_dir = BASE_DIR / "app" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Initialize database on startup (serverless-compatible)
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize database: {e}")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(events.router)

# Update the root function
@app.get("/")
async def root(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_optional_user) # <--- Check for user
):
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "user": user # <--- Pass it to the template
        }
    )