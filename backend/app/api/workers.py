from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Worker, Candidate
from app.schemas.schemas import Worker as WorkerSchema, WorkerCreate, WorkerUpdate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[WorkerSchema])
def read_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "OWNER" or current_user.role == "FINANCE":
        return db.query(Worker).filter(Worker.is_deleted == False).offset(skip).limit(limit).all()
    elif current_user.role == "CURATOR":
        admin_ids = [admin.id for admin in current_user.admins]
        return db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.admin_id.in_(admin_ids)).offset(skip).limit(limit).all()
    elif current_user.role == "ADMIN":
        return db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.admin_id == current_user.id).offset(skip).limit(limit).all()
    return []

@router.post("/", response_model=WorkerSchema)
def create_worker(worker_in: WorkerCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    candidate = db.query(Candidate).filter(Candidate.id == worker_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if current_user.role == "ADMIN" and candidate.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your candidate")
        
    worker = Worker(
        candidate_id=worker_in.candidate_id,
        admin_id=candidate.admin_id,
        partner_id=worker_in.partner_id,
        status=worker_in.status
    )
    db.add(worker)
    candidate.status = "WORKER" # Auto-update candidate status
    db.commit()
    db.refresh(worker)
    log_audit(db, current_user.id, "CREATE", "Worker", worker.id, {"status": worker.status})
    return worker

@router.patch("/{worker_id}/status", response_model=WorkerSchema)
def update_worker_status(worker_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    if current_user.role == "ADMIN" and worker.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your worker")
        
    worker.status = status
    db.commit()
    db.refresh(worker)
    log_audit(db, current_user.id, "CHANGE_STATUS", "Worker", worker.id, {"status": status})
    return worker

@router.get("/{worker_id}", response_model=WorkerSchema)
def get_worker(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    if current_user.role == "ADMIN" and worker.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your worker")
    
    return worker

@router.patch("/{worker_id}/partner", response_model=WorkerSchema)
def update_worker_partner(worker_id: int, partner_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    worker.partner_id = partner_id
    db.commit()
    db.refresh(worker)
    log_audit(db, current_user.id, "UPDATE", "Worker", worker.id, {"partner_id": partner_id})
    return worker


@router.patch("/{worker_id}/admin", response_model=WorkerSchema)
def update_worker_admin(worker_id: int, admin_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    worker.admin_id = admin_id
    # Also update the linked candidate to keep it consistent
    if worker.candidate:
        worker.candidate.admin_id = admin_id
        
    db.commit()
    db.refresh(worker)
    log_audit(db, current_user.id, "UPDATE", "Worker", worker.id, {"admin_id": admin_id})
    return worker

@router.delete("/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    worker.is_deleted = True
    import datetime
    worker.deleted_at = datetime.datetime.utcnow()
    log_audit(db, current_user.id, "DELETE", "Worker", worker_id, {})
    db.commit()
    return {"status": "success"}
