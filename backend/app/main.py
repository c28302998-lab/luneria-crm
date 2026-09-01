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
    from sqlalchemy import text
    from app.models.telegram import Base
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE telegram_accounts ADD COLUMN mask_client_names BOOLEAN DEFAULT FALSE"))
    except Exception:
        pass
