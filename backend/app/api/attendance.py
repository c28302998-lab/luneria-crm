from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.db.database import get_db
from app.models.models import User, Attendance, Worker
from app.schemas.schemas import Attendance as AttendanceSchema, AttendanceCreate
from app.core.dependencies import get_current_user, RoleChecker

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
        record.updated_by = current_user.id
    else:
        record = Attendance(
            worker_id=attendance_in.worker_id,
            date=attendance_in.date,
            is_present=attendance_in.is_present,
            updated_by=current_user.id
        )
        db.add(record)
        
    db.commit()
    db.refresh(record)
    return record
