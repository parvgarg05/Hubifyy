from app.db.database import SessionLocal, engine, Base
from app.db.models import User, Club, Event
from app.core.security import get_password_hash
from datetime import datetime, timedelta

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_data():
    if db.query(User).filter(User.email == "admin@hubify.com").first():
        print("✅ Data already exists!")
        return

    print("🌱 Seeding database...")

    # 1. Create Admin
    admin = User(
        email="admin@hubify.com",
        full_name="College Admin",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    # 2. Create Clubs
    club_tech = Club(
        name="GDG JIIT Noida",
        description="Google Developer Groups - AI, Cloud, and Web.",
        logo_url="https://via.placeholder.com/100",
        admin_id=admin.id
    )
    club_sports = Club(
        name="JIIT Cricket Club",
        description="Weekly matches and tournaments.",
        logo_url="https://via.placeholder.com/100",
        admin_id=admin.id
    )
    db.add_all([club_tech, club_sports])
    db.commit()

    # 3. Create Events
    events = [
        Event(title="Tech Summit 2026", description="Generative AI & LLMs.", date_time=datetime.now() + timedelta(days=5), location="Auditorium", club_id=club_tech.id),
        Event(title="Cricket Finals", description="JIIT vs Sector 128.", date_time=datetime.now() + timedelta(days=10), location="Sports Ground", club_id=club_sports.id),
        Event(title="FastAPI Workshop", description="Learn Backend Dev.", date_time=datetime.now() + timedelta(days=12), location="Lab 4", club_id=club_tech.id)
    ]
    db.add_all(events)
    db.commit()

    print("✅ Database populated!")
    print("---------------------------------")
    print("Login as Admin: admin@hubify.com / admin123")
    print("---------------------------------")

if __name__ == "__main__":
    seed_data()