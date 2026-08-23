import sys
import os

from app.db.database import SessionLocal, engine, Base
from app.models.models import User, Candidate, Worker, Partner, Payment, Task
from app.core.security import get_password_hash

def seed():
    # CREATE TABLES
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if owner already exists
        existing_owner = db.query(User).filter(User.email == "owner@luneria.local").first()
        if existing_owner:
            print("Database already seeded!")
            return

        # 1 Owner
        owner = User(
            name="Owner User",
            email="owner@luneria.local",
            password_hash=get_password_hash("password123"),
            role="OWNER"
        )
        db.add(owner)
        
        # 1 Finance
        finance = User(
            name="Finance User",
            email="finance@luneria.local",
            password_hash=get_password_hash("password123"),
            role="FINANCE"
        )
        db.add(finance)
        
        # 2 Curators
        curator1 = User(
            name="Curator 1",
            email="curator1@luneria.local",
            password_hash=get_password_hash("password123"),
            role="CURATOR"
        )
        db.add(curator1)
        
        db.commit()
        
        # 6 Admins (3 for each curator)
        for i in range(1, 4):
            admin = User(
                name=f"Admin {i}",
                email=f"admin{i}@luneria.local",
                password_hash=get_password_hash("password123"),
                role="ADMIN",
                curator_id=curator1.id
            )
            db.add(admin)
        db.commit()

        print("Seed completed successfully!")
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
