from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.db.database import get_db
from app.models.models import Notification, User, Attendance, Worker
from app.schemas.schemas import Attendance as AttendanceSchema, AttendanceCreate
from app.core.dependencies import get_current_user, RoleChecker

from app.models.models import Notification, Candidate
from pydantic import BaseModel

class VerifyShiftRequest(BaseModel):
    is_present: bool
router = APIRouter()

@router.get("/", response_model=List[AttendanceSchema])
def get_attendance(target_date: date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Everyone can view attendance
    query = db.query(Attendance).filter(Attendance.date == target_date)
    return query.all()

@router.post("/", response_model=AttendanceSchema)
def set_attendance(attendance_in: AttendanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    worker = db.query(Worker).filter(Worker.id == attendance_in.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    # Check permissions: Owner can edit all, Admin can edit their own
    if current_user.role == "CURATOR":
        raise HTTPException(status_code=403, detail="Curators cannot edit attendance")
    if current_user.role == "ADMIN" and worker.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit attendance for your own workers")
        
    # Find existing record
    record = db.query(Attendance).filter(
        Attendance.worker_id == attendance_in.worker_id,
        Attendance.date == attendance_in.date
    ).first()
    
    if record:
        record.is_present = attendance_in.is_present
        record.status = 'APPROVED'
        record.updated_by = current_user.id
        if current_user.role == "OWNER" and hasattr(attendance_in, "income"):
            record.income = attendance_in.income
    else:
        record = Attendance(
            worker_id=attendance_in.worker_id,
            date=attendance_in.date,
            is_present=attendance_in.is_present,
            status='APPROVED',
            updated_by=current_user.id
        )
        if current_user.role == "OWNER" and hasattr(attendance_in, "income"):
            record.income = attendance_in.income
        db.add(record)
        
    db.commit()
    db.refresh(record)
    return record



@router.get("/today-status")
def get_today_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "WORKER":
        return {"status": "NOT_WORKER"}
    
    from app.models.models import Notification, Candidate, Worker
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if not candidate:
        return {"status": "NO_CANDIDATE"}
        
    worker = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
    if not worker:
        return {"status": "NO_WORKER"}
        
    today = date.today()
    record = db.query(Attendance).filter(Attendance.worker_id == worker.id, Attendance.date == today).first()
    
    if not record:
        return {"status": "NOT_STARTED"}
    
    return {
        "status": record.status,
        "is_present": record.is_present
    }

@router.get("/pending", response_model=List[AttendanceSchema])
def get_pending_attendance(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    if current_user.role == "ADMIN":
        workers = db.query(Worker).filter(Worker.admin_id == current_user.id).all()
        worker_ids = [w.id for w in workers]
        return db.query(Attendance).filter(Attendance.status == "PENDING", Attendance.worker_id.in_(worker_ids)).all()
    else:
        return db.query(Attendance).filter(Attendance.status == "PENDING").all()

@router.post("/start-shift", response_model=AttendanceSchema)
def start_shift(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "WORKER":
        raise HTTPException(status_code=403, detail="Only workers can start shift")
        
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found for your email")
        
    worker = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    today = date.today()
    record = db.query(Attendance).filter(Attendance.worker_id == worker.id, Attendance.date == today).first()
    if record:
        raise HTTPException(status_code=400, detail="Shift already started or marked today")
        
    record = Attendance(
        worker_id=worker.id,
        date=today,
        is_present=False,
        status="PENDING",
        updated_by=current_user.id
    )
    db.add(record)
    
    # Send notification to Admin
    if worker.admin_id:
        notif = Notification(
            user_id=worker.admin_id,
            type="Выход на смену",
            message=f"Работник {candidate.first_name} ({current_user.email}) вышел на смену и ждет подтверждения."
        )
        db.add(notif)
        
    db.commit()
    db.refresh(record)
    return record

@router.put("/{attendance_id}/verify", response_model=AttendanceSchema)
def verify_shift(attendance_id: int, req: VerifyShiftRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    worker = db.query(Worker).filter(Worker.id == record.worker_id).first()
    if current_user.role == "ADMIN" and worker.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your worker")
        
    record.is_present = req.is_present
    record.status = "APPROVED" if req.is_present else "REJECTED"
    record.updated_by = current_user.id
    db.commit()
    db.refresh(record)
    return record
