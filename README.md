# Hubify - College Clubs & Community Hub

Hubify is a FastAPI web application for managing college clubs, events, registrations, and admin workflows. It uses Jinja2 templates for the UI, SQLAlchemy for persistence, and supports role-based access for students and admins.

## Features

- Student and admin authentication
- Club and event management
- Event registration flow
- Admin dashboard for content management
- Server-rendered pages with FastAPI + Jinja2

## Tech Stack

- FastAPI
- SQLAlchemy
- Jinja2
- Uvicorn
- MySQL or SQLite, depending on `DATABASE_URL`

## Project Structure

- `main.py` - FastAPI entrypoint
- `app/core/` - configuration, dependencies, and security helpers
- `app/db/` - database engine, session, and ORM models
- `app/routers/` - route modules for auth, admin, clubs, and events
- `app/templates/` - HTML templates
- `app/static/` - CSS and JavaScript assets
- `seed.py` - sample data seeding script
- `check_db.py` - simple database inspection script

## Prerequisites

- Python 3.10 or newer
- A database connection string

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the required values:

```env
DATABASE_URL=sqlite:///./college_hub.db
SECRET_KEY=change-this-to-a-secure-random-string
```

You can also point `DATABASE_URL` to MySQL if you prefer that backend.

## Run the App

Start the development server with Uvicorn:

```bash
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000` in your browser.

## Seed Sample Data

Populate the database with demo content:

```bash
python seed.py
```

The seed script creates an admin account:

- Email: `admin@hubify.com`
- Password: `admin123`

## Check the Database

You can inspect the local SQLite database with:

```bash
python check_db.py
```

## Notes

- Tables are created automatically when the app starts.
- The app mounts static assets from `app/static` and templates from `app/templates`.
- The main data models are `User`, `Club`, and `Event`.