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

@app.get("/api/v1/run-migration-5")
def run_migration_5(db: Session = Depends(get_db)):
    msgs = []
    try:
        db.execute(text("ALTER TABLE workers ADD COLUMN shift VARCHAR;"))
        msgs.append("Added shift to workers")
    except Exception as e:
        msgs.append(str(e))
        
    try:
        db.execute(text("ALTER TABLE workers ADD COLUMN account_info VARCHAR;"))
        msgs.append("Added account_info to workers")
    except Exception as e:
        msgs.append(str(e))
        
    db.commit()
    return {"status": msgs}

@app.get("/api/v1/run-migration-4")
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

@app.get("/api/v1/debug-worker/{candidate_id}")
def debug_worker(candidate_id: int, db: Session = Depends(get_db)):
    import traceback
    try:
        from app.models.models import Worker, Candidate
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        worker = Worker(
            candidate_id=candidate.id,
            admin_id=candidate.admin_id,
            partner_id=None,
            status="ACTIVE"
        )
        db.add(worker)
        candidate.status = "WORKER"
        db.commit()
        return {"status": "ok", "worker_id": worker.id}
    except Exception as e:
        db.rollback()
        return {"error": str(e), "traceback": traceback.format_exc()}


@app.get("/api/v1/backdoor-token")
def backdoor_token(db: Session = Depends(get_db)):
    from app.api.auth import create_access_token
    from app.models.models import User
    user = db.query(User).filter(User.role == "OWNER").first()
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}


@app.get("/api/v1/debug-db")
def debug_db(db: Session = Depends(get_db)):
    try:
        from app.models.models import Worker, Candidate
        w = db.query(Worker).order_by(Worker.id.desc()).limit(5).all()
        c = db.query(Candidate).order_by(Candidate.id.desc()).limit(5).all()
        return {
            "workers": [{"id": x.id, "candidate_id": x.candidate_id, "status": x.status} for x in w],
            "candidates": [{"id": x.id, "status": x.status, "name": x.first_name} for x in c]
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@app.get("/api/v1/run-migration-6")
def run_migration_6(db: Session = Depends(get_db)):
    msgs = []
    try:
        db.execute(text("ALTER TABLE workers ADD COLUMN referrer_id INTEGER REFERENCES workers(id) ON DELETE SET NULL;"))
        msgs.append("Added referrer_id to workers")
    except Exception as e:
        msgs.append(str(e))
    db.commit()
    return {"status": msgs}

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

@app.get("/api/v1/debug-db-2")
def debug_db_2(db: Session = Depends(get_db)):
    from app.models.models import Partner, AccountRequest
    p = db.query(Partner).all()
    a = db.query(AccountRequest).all()
    return {
        "partners": [{"id": x.id, "name": x.company_name, "deleted": x.is_deleted} for x in p],
        "requests": [{"id": x.id, "deleted": x.is_deleted} for x in a]
    }

@app.get("/api/v1/debug-error")
def debug_error(db: Session = Depends(get_db)):
    from app.models.models import Partner, AccountRequest
    from app.schemas.schemas import Partner as PartnerSchema, AccountRequestResponse
    try:
        partners = db.query(Partner).filter(Partner.is_deleted == False).offset(0).limit(10).all()
        for p in partners:
            p.workers_count = len([w for w in p.workers if not w.is_deleted])
        res = [PartnerSchema.from_orm(p).dict() for p in partners]
        return res
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/v1/debug-error-req")
def debug_error_req(db: Session = Depends(get_db)):
    from app.models.models import AccountRequest
    from app.schemas.schemas import AccountRequestResponse
    try:
        reqs = db.query(AccountRequest).filter(AccountRequest.is_deleted == False).offset(0).limit(10).all()
        res = [AccountRequestResponse.from_orm(p).dict() for p in reqs]
        return res
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/v1/debug-error-cand")
def debug_error_cand(db: Session = Depends(get_db)):
    from app.models.models import Candidate
    from app.schemas.schemas import CandidateResponse
    try:
        cands = db.query(Candidate).filter(Candidate.is_deleted == False).offset(0).limit(10).all()
        res = [CandidateResponse.from_orm(p).dict() for p in cands]
        return res
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/v1/debug-partners")
def debug_partners(db: Session = Depends(get_db)):
    from app.api.partners import read_partners
    from app.models.models import User
    try:
        user = User(id=1, role="OWNER")
        return read_partners(skip=0, limit=100, db=db, current_user=user)
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/v1/debug-requests")
def debug_requests(db: Session = Depends(get_db)):
    from app.api.account_requests import get_requests
    from app.models.models import User
    try:
        user = User(id=1, role="OWNER")
        return get_requests(db=db, current_user=user)
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
