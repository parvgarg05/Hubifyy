"""
Admin dashboard routes for managing clubs and events.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_current_admin
from app.db.database import get_db
from app.db.models import User, Club, Event

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Create admin router
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def admin_dashboard(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Render admin dashboard with clubs and events stats."""
    clubs = db.query(Club).all()
    events = db.query(Event).all()
    
    total_clubs = len(clubs)
    total_events = len(events)
    total_users = db.query(User).count()
    
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "user": current_admin,
            "clubs": clubs,
            "events": events,
            "total_clubs": total_clubs,
            "total_events": total_events,
            "total_users": total_users
        }
    )


@router.post("/clubs")
async def create_club(
    name: str = Form(...),
    description: str = Form(""),
    logo_url: str = Form(""),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new club."""
    if not name or len(name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Club name cannot be empty"
        )
    
    new_club = Club(
        name=name.strip(),
        description=description.strip() if description else None,
        logo_url=logo_url.strip() if logo_url else None,
        admin_id=current_admin.id
    )
    
    db.add(new_club)
    db.commit()
    
    return RedirectResponse(
        url="/admin/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/events")
async def create_event(
    title: str = Form(...),
    description: str = Form(""),
    date_time: str = Form(...),
    location: str = Form(""),
    registration_link: str = Form(None), # <--- Capturing Google Form link
    club_id: int = Form(...),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new event."""
    if not title or len(title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Title required")
    
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    try:
        event_dt = datetime.fromisoformat(date_time)
    except ValueError:
        event_dt = datetime.now()

    new_event = Event(
        title=title.strip(),
        description=description.strip() if description else None,
        date_time=event_dt,
        location=location.strip() if location else "",
        registration_link=registration_link.strip() if registration_link else None, # <--- Saving it
        club_id=club_id
    )
    
    db.add(new_event)
    db.commit()
    
    return RedirectResponse(
        url="/admin/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )


# --- EVENT MANAGEMENT ---

@router.post("/events/{event_id}/delete")
async def delete_event(
    event_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.get("/events/{event_id}/edit")
async def edit_event_page(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Show the edit event form."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    clubs = db.query(Club).all()
    
    return templates.TemplateResponse(
        "edit_event.html",
        {
            "request": request, 
            "event": event, 
            "clubs": clubs,
            "user": current_admin
        }
    )


@router.post("/events/{event_id}/edit")
async def update_event(
    event_id: int,
    title: str = Form(...),
    description: str = Form(None),
    club_id: int = Form(...),
    date_time: str = Form(...),
    location: str = Form(None),
    registration_link: str = Form(None), # <--- Capture link in edit mode
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Save changes to an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.title = title
    event.description = description.strip() if description else None
    event.club_id = club_id
    event.date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
    event.location = location.strip() if location else ""
    event.registration_link = registration_link.strip() if registration_link else None # <--- Update link

    db.commit()

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )

# --- CLUB MANAGEMENT ---

@router.post("/clubs/{club_id}/delete")
async def delete_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Delete a club."""
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    db.delete(club)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.get("/clubs/{club_id}/edit")
async def edit_club_page(
    request: Request,
    club_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Show the edit club form."""
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    return templates.TemplateResponse(
        "edit_club.html", 
        {
            "request": request, 
            "club": club,
            "user": current_admin
        }
    )


@router.post("/clubs/{club_id}/edit")
async def update_club(
    club_id: int,
    name: str = Form(...),
    description: str = Form(None),
    logo_url: str = Form(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Save changes to a club."""
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    club.name = name.strip()
    club.description = description.strip() if description else None
    club.logo_url = logo_url.strip() if logo_url else None
    
    db.commit()

    return RedirectResponse(url="/admin/dashboard", status_code=303)