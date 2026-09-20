from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api import auth, telegram_admin, telegram_proxy
from app.api import automation
from app.api import shifts
from app.api import reviews
import os


from sqlalchemy import text


app = FastAPI(
    title="Lunery CRM API",
    description="Internal CRM system for Lunery agency",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.api.router import api_router


@app.get("/api/migrate-old-reports")
def migrate_old_reports(db: Session = Depends(get_db)):
    from app.models.models import ShiftReport, Shift
    reports = db.query(ShiftReport).all()
    count = 0
    for r in reports:
        # Check if already migrated
        existing = db.query(Shift).filter(Shift.worker_id == r.worker_id, Shift.start_time == r.created_at).first()
        if not existing:
            status_map = {"PENDING": "PENDING_REVIEW", "APPROVED": "APPROVED", "REJECTED": "REJECTED"}
            s = Shift(
                worker_id=r.worker_id,
                admin_id=None,
                shift_type="DAY",
                start_time=r.created_at,
                end_time=r.created_at,
                status=status_map.get(r.status, "PENDING_REVIEW"),
                report_data={
                    "amount": r.amount,
                    "screenshot": r.files[0] if r.files else None,
                    "notes": r.notes,
                    "worker_amount": r.worker_amount,
                    "admin_amount": r.admin_amount
                },
                stats={"balance": r.amount}
            )
            db.add(s)
            count += 1
    db.commit()
    return {"migrated": count, "total": len(reports)}

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews"])
app.include_router(shifts.router, prefix="/api/v1/shifts", tags=["Shifts"])
app.include_router(automation.router, prefix="/api/v1/automation", tags=["Automation"])
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Lunery CRM API"}

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
    from app.db.database import engine, Base
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
    
    migrations = [
        "ALTER TABLE partners ADD COLUMN country VARCHAR;",
        "ALTER TABLE partners ADD COLUMN seats INTEGER DEFAULT 0;",
        "ALTER TABLE partners ADD COLUMN payment_terms VARCHAR;",
        "ALTER TABLE partners ADD COLUMN experience VARCHAR;",
        "ALTER TABLE partners ADD COLUMN registration_time VARCHAR;",
        "ALTER TABLE partners ADD COLUMN response_time VARCHAR;",
        "ALTER TABLE partners ADD COLUMN rating FLOAT;",
        "ALTER TABLE partners ADD COLUMN last_contact_date VARCHAR;",
        "ALTER TABLE partners ADD COLUMN advances VARCHAR;",
        "ALTER TABLE partners ADD COLUMN schedules VARCHAR;",
        "ALTER TABLE users ADD COLUMN raw_password VARCHAR;",
        "ALTER TABLE telegram_accounts ADD COLUMN worker_note TEXT;",
        "ALTER TABLE telegram_accounts ADD COLUMN mask_client_names BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE telegram_accounts ADD COLUMN assigned_worker_id INTEGER;",
        "ALTER TABLE telegram_accounts ADD COLUMN responsible_admin_id INTEGER;",
                "ALTER TABLE email_accounts ADD COLUMN assigned_admin_id INTEGER;",
        "ALTER TABLE telegram_accounts ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE telegram_accounts ADD COLUMN deleted_at TIMESTAMP;",
        "ALTER TABLE email_accounts ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE email_accounts ADD COLUMN deleted_at TIMESTAMP;"
    ]
    
    with engine.connect() as conn:
        for query in migrations:
            try:
                conn.execute(text(query))
                conn.commit()
            except Exception as e:
                conn.rollback()


