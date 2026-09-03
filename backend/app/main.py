from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api import auth, telegram_admin, telegram_proxy
import os





app = FastAPI(
    title="Luneria CRM API",
    description="Internal CRM system for Luneria agency",
    version="1.0.0"
)

from sqlalchemy import text
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

@app.get("/api/v1/run-migration-3")

@app.get("/api/v1/run-migration-4")
def run_migration_4(db: Session = Depends(get_db)):
    msgs = []
    try:
        db.execute(text("ALTER TABLE candidate_history ADD COLUMN referrer_id INTEGER REFERENCES workers(id) ON DELETE SET NULL;"))
        msgs.append("Added referrer_id to candidate_history")
    except Exception as e:
        msgs.append(str(e))
        
    try:
        db.execute(text("ALTER TABLE trainings ADD COLUMN referrer_id INTEGER REFERENCES workers(id) ON DELETE SET NULL;"))
        msgs.append("Added referrer_id to trainings")
    except Exception as e:
        msgs.append(str(e))
        
    db.commit()
    return {"status": msgs}

@app.get("/api/v1/run-migration-3")
def run_migration_3(db: Session = Depends(get_db)):
    msgs = []
    try:
        db.execute(text("ALTER TABLE attendance ADD COLUMN income FLOAT;"))
        msgs.append("Added income")
    except Exception as e:
        msgs.append(str(e))
        
    try:
        db.execute(text("ALTER TABLE accounts ADD COLUMN gmail_address VARCHAR;"))
        db.execute(text("ALTER TABLE accounts ADD COLUMN gmail_password VARCHAR;"))
        msgs.append("Added gmail")
    except Exception as e:
        msgs.append(str(e))
        
    try:
        db.execute(text("ALTER TABLE workers ADD COLUMN referrer_id INTEGER REFERENCES workers(id) ON DELETE SET NULL;"))
        msgs.append("Added referrer_id")
    except Exception as e:
        msgs.append(str(e))
        
    db.commit()
    return {"status": msgs}


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.api.router import api_router

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix="/api/v1")
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Luneria CRM API"}

@app.get("/api/v1/run-seed")
def run_seed_endpoint():
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        import seed
        seed.seed()
        return {"status": "Database seeded successfully!"}
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}

@app.on_event("startup")
def auto_migrate():
    from app.db.database import engine
