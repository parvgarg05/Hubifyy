"""
Club management routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_current_admin
from app.db.database import get_db
from app.db.models import Club, User
from app.schemas import ClubCreate, ClubResponse, ClubDetailResponse


router = APIRouter(prefix="/clubs", tags=["clubs"])


@router.get("", response_model=list[ClubResponse])
async def list_clubs(db: Session = Depends(get_db)):
    """
    Get list of all clubs.
    
    Returns:
        List of all clubs
    """
    clubs = db.query(Club).all()
    return clubs


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    club_data: ClubCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new club. Admin only.
    
    Args:
        club_data: Club creation data
        current_admin: Currently authenticated admin user
        db: Database session
        
    Returns:
        Created club object
    """
    new_club = Club(
        name=club_data.name,
        description=club_data.description,
        logo_url=club_data.logo_url,
        admin_id=current_admin.id
    )
    
    db.add(new_club)
    db.commit()
    db.refresh(new_club)
    
    return new_club


@router.get("/{club_id}", response_model=ClubDetailResponse)
async def get_club_detail(
    club_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific club.
    
    Args:
        club_id: Club ID
        db: Database session
        
    Returns:
        Club details with admin info and events
        
    Raises:
        HTTPException: 404 if club not found
    """
    club = db.query(Club).filter(Club.id == club_id).first()
    
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    return club
