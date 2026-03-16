"""
Hubify - College Clubs & Community Hub
FastAPI Application Entry Point
"""

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

# This line creates the tables if they don't exist
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create database tables on startup: {e}")
    print("Database will be created when needed or on first request.")

app = FastAPI()
# Create FastAPI application
app = FastAPI(
    title="Hubify",
    description="College Clubs & Community Hub",
    version="1.0.0"
)

# 1. Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 2. Setup Templates (This tells FastAPI where to find index.html)
templates = Jinja2Templates(directory="app/templates")

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