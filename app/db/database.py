"""
Database connection and session management.

Works on both local development and Vercel serverless environment.
For Vercel: Uses PostgreSQL (Neon) instead of SQLite for production.
For Local: Uses SQLite with optional PostgreSQL.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base for ORM models."""
    pass


# Create database engine
# Check if we are using SQLite (the URL starts with "sqlite")
if settings.DATABASE_URL.startswith("sqlite"):
    # For SQLite: Ensure the database file is in /tmp for Vercel compatibility
    # In local environment, this will create .db in project root
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    # If running on Vercel, redirect SQLite to /tmp (ephemeral storage)
    if os.environ.get("VERCEL"):
        db_path = f"/tmp/{Path(db_path).name}"
        database_url = f"sqlite:///{db_path}"
    else:
        database_url = settings.DATABASE_URL
    
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}  # REQUIRED for SQLite
    )
else:
    # For PostgreSQL (Neon) and other databases
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_recycle=3600,   # Recycle connections every hour
    )

# Create sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
