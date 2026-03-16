"""
Vercel Serverless Function Entry Point

Vercel automatically looks for /api/index.py and exports the ASGI application.
This imports the FastAPI app from main.py and exposes it for Vercel.
"""

# Import the FastAPI app from main module
from main import app

# Vercel expects the ASGI app to be the default export
# This will be used as the serverless function handler
__all__ = ["app"]
