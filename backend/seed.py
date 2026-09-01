import sys
import os

from app.db.database import SessionLocal, engine, Base
from app.models.telegram import TelegramAccount, TelegramRequest, TelegramAuditLog
from app.models.models import User, Candidate, Worker, Partner, Payment, Task
from app.core.security import get_password_hash

def seed():
    # CREATE TABLES
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            # Add columns if missing
            tables = ['payments', 'reports', 'tasks', 'workers', 'expenses', 'candidates']
            for table in tables:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS files JSON DEFAULT '[]';"))
                # Update existing nulls
                conn.execute(text(f"UPDATE {table} SET files = '[]' WHERE files IS NULL;"))
            

            conn.execute(text("ALTER TABLE notifications ADD COLUMN IF NOT EXISTS type VARCHAR;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS candidate_name VARCHAR;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS age VARCHAR;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS account_type VARCHAR;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS admin_nickname VARCHAR;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS candidate_nickname VARCHAR;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS candidate_tg VARCHAR;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS questionnaire VARCHAR;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS partner_id INTEGER;"))
            conn.execute(text("ALTER TABLE account_requests ADD COLUMN IF NOT EXISTS issued_account_name VARCHAR;"))

        try:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id SERIAL PRIMARY KEY,
                    login VARCHAR NOT NULL,
                    worker_id INTEGER REFERENCES workers(id),
                    partner_id INTEGER REFERENCES partners(id),
                    issued_at TIMESTAMP,
                    status VARCHAR DEFAULT 'FREE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE
                )
            '''))
            print("accounts table ensured")
        except Exception as e:
            print(f"Migration error for accounts: {e}")

        try:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN IF NOT EXISTS account_number VARCHAR;"))
            print("accounts account_number added")
        except Exception as e:
            print(f"Migration error: {e}")

        try:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS account_emails (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR NOT NULL,
                    account_id INTEGER REFERENCES accounts(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE
                )
            '''))
            print("account_emails table ensured")
        except Exception as e:
            print(f"Migration error for account_emails: {e}")

        try:
            conn.execute(text("ALTER TABLE account_emails ADD COLUMN IF NOT EXISTS linked_account_name VARCHAR;"))
            print("account_emails linked_account_name added")
        except Exception as e:
            print(f"Migration error: {e}")



            
            # Add new columns for attendance and shift
            conn.execute(text("ALTER TABLE workers ADD COLUMN IF NOT EXISTS shift VARCHAR;"))
            conn.execute(text("ALTER TABLE workers ADD COLUMN IF NOT EXISTS account_info VARCHAR;"))
            
            # Note: sources and materials are created by create_all()
            conn.commit()

    except Exception as e:
        print("Error altering tables:", e)


    
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
