from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User, Shift, Worker, AuditLog, Candidate
from app.core.dependencies import get_current_user, RoleChecker
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ShiftStartRequest(BaseModel):
    shift_type: str = "DAY" # DAY, NIGHT

class ShiftEndRequest(BaseModel):
    report_data: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = None

@router.post("/start")
def start_shift(req: ShiftStartRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["WORKER"]))):
    # Check if active shift exists
    active = db.query(Shift).filter(Shift.worker_id == current_user.id, Shift.status == "ACTIVE").first()
    if active:
        raise HTTPException(status_code=400, detail="У вас уже есть активная смена")
        
    # Find worker via Candidate email
    from app.models.models import Candidate
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    worker = None
    if candidate:
        worker = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
    admin_id = worker.admin_id if worker else None

    shift = Shift(
        worker_id=current_user.id,
        admin_id=admin_id,
        shift_type=req.shift_type,
        start_time=datetime.utcnow(),
        status="ACTIVE"
    )
    db.add(shift)
    
    log = AuditLog(
        user_id=current_user.id,
        action="SHIFT_START",
        details=f"Started {req.shift_type} shift"
    )
    db.add(log)
    
    db.commit()
    db.refresh(shift)
    return shift

@router.post("/end")
def end_shift(req: ShiftEndRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["WORKER"]))):
    active = db.query(Shift).filter(Shift.worker_id == current_user.id, Shift.status == "ACTIVE").first()
    if not active:
        raise HTTPException(status_code=400, detail="Нет активной смены")
        
    active.end_time = datetime.utcnow()
    
    active.status = "PENDING_REVIEW"
    
    # Also update google sheets with shift date
    active_assignments = db.query(AccountAssignment).filter(AccountAssignment.worker_id == user_id, AccountAssignment.revoked_at == None).all()
    if active_assignments:
        acc_ids = [a.account_id for a in active_assignments]
        now_str = datetime.utcnow().strftime("%d.%m.%Y")
        bg_tasks.add_task(set_shift_date_for_accounts, acc_ids, now_str)

    active.report_data = req.report_data
    active.stats = req.stats
    
    log = AuditLog(
        user_id=current_user.id,
        action="SHIFT_END",
        details=f"Ended shift and submitted report for review"
    )
    db.add(log)
    
    db.commit()
    db.refresh(active)
    return active

from pydantic import BaseModel
class ShiftApproveRequest(BaseModel):
    worker_amount: float
    admin_amount: float

@router.post("/{shift_id}/approve")
def approve_shift(shift_id: int, payload: ShiftApproveRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
        
    if shift.status != "PENDING_REVIEW":
        raise HTTPException(status_code=400, detail="Shift is not pending review")
        
    shift.status = "APPROVED"
    
    # Add money
    worker_user = None
    worker = db.query(Worker).filter(Worker.id == shift.worker_id).first()
    if worker:
        candidate = db.query(Candidate).filter(Candidate.id == worker.candidate_id).first()
        if candidate and candidate.email:
            worker_user = db.query(User).filter(User.email == candidate.email).first()
            
    if worker_user:
        worker_user.balance = (worker_user.balance or 0.0) + payload.worker_amount
        if worker.admin_id:
            admin_user = db.query(User).filter(User.id == worker.admin_id).first()
            if admin_user:
                admin_user.balance = (admin_user.balance or 0.0) + payload.admin_amount

    
    log = AuditLog(
        user_id=current_user.id,
        action="SHIFT_APPROVED",
        details=f"Approved shift {shift.id} for worker {shift.worker_id}"
    )
    db.add(log)
    
    db.commit()
    return {"message": "Смена одобрена"}

@router.get("/my")
def get_my_shifts(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["WORKER"]))):
    return db.query(Shift).filter(Shift.worker_id == current_user.id).order_by(Shift.start_time.desc()).all()

@router.get("/pending")
def get_pending_shifts(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    query = db.query(Shift).filter(Shift.status == "PENDING_REVIEW")
    if current_user.role == "ADMIN":
        query = query.filter(Shift.admin_id == current_user.id)
    return query.order_by(Shift.end_time.desc()).all()


@router.get("/all")
def get_all_shifts(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    query = db.query(Shift).filter(Shift.status != "ACTIVE") # Show all completed/pending/approved
    if current_user.role == "ADMIN":
        query = query.filter(Shift.admin_id == current_user.id)
    return query.order_by(Shift.start_time.desc()).limit(200).all()
