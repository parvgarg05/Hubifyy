"""
Events and student-facing routes.
"""

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Import the new dependency
from app.core.deps import get_current_user, get_optional_user
from app.db.database import get_db
from app.db.models import Event, User, Club

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/clubs")
def list_clubs(
    request: Request, 
    db: Session = Depends(get_db),
    # Check if user is logged in (but don't force it)
    current_user: User = Depends(get_optional_user) 
):
    clubs = db.query(Club).all()
    return templates.TemplateResponse(
        "clubs.html", 
        {
            "request": request, 
            "clubs": clubs, 
            "user": current_user  # <--- PASS USER TO TEMPLATE
        }
    )

@router.get("/events")
async def list_events(
    request: Request,
    db: Session = Depends(get_db),
    # Check if user is logged in (but don't force it)
    current_user: User = Depends(get_optional_user)
):
    """Public listing of all events."""
    events = db.query(Event).all()
    return templates.TemplateResponse(
        "events.html",
        {
            "request": request,
            "events": events,
            "user": current_user # <--- PASS USER TO TEMPLATE
        },
    )

@router.get("/dashboard")
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user), # Keep strict check for dashboard
    db: Session = Depends(get_db)
):
    """Render student dashboard with registered events."""
    my_events = (
        db.query(Event)
        .join(Event.registered_users)
        .filter(User.id == user.id)
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "my_events": my_events,
        },
    )

@router.post("/events/{event_id}/register")
async def register_for_event(
    event_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register current user for an event and redirect to Google Form if available."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # 1. Register them locally if not already registered
    if user not in event.registered_users:
        event.registered_users.append(user)
        db.commit()

    # 2. Check if a Google Form link exists
    # If it exists, redirect to the form. If not, go to the dashboard.
    if event.registration_link:
        return RedirectResponse(
            url=event.registration_link,
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(
        url="/dashboard",
        status_code=status.HTTP_303_SEE_OTHER,
    )

# --- Add this to app/routers/events.py ---

@router.get("/clubs/{club_id}/events")
async def list_club_specific_events(
    club_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """List events ONLY for a specific club."""
    # 1. Get the club info (so we can show the name "Robotics Club Events")
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    # 2. Get events ONLY for this club
    events = db.query(Event).filter(Event.club_id == club_id).all()

    # 3. Reuse the existing events.html template!
    return templates.TemplateResponse(
        "events.html",
        {
            "request": request,
            "events": events,
            "user": current_user,
            "club": club,  # Pass the club so the template knows to change the title
            "filter_mode": True # A flag to tell the UI "We are in filter mode"
        },
    )