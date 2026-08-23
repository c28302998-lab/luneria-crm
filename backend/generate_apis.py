import os

base_dir = "/Users/thf/.gemini/antigravity/scratch/luneria/backend/app/api"

files = {
    "trainings.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Training
from app.schemas.schemas import Training as TrainingSchema, TrainingUpdate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/{candidate_id}", response_model=TrainingSchema)
def read_training(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    training = db.query(Training).filter(Training.candidate_id == candidate_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    return training

@router.put("/{training_id}", response_model=TrainingSchema)
def update_training(training_id: int, training_in: TrainingUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
        
    for key, value in training_in.dict(exclude_unset=True).items():
        setattr(training, key, value)
        
    db.commit()
    db.refresh(training)
    log_audit(db, current_user.id, "UPDATE", "Training", training.id, {"progress": training.progress})
    return training
""",
    "reports.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Report
from app.schemas.schemas import Report as ReportSchema, ReportCreate
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ReportSchema])
def read_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "OWNER":
        return db.query(Report).offset(skip).limit(limit).all()
    else:
        return db.query(Report).filter(Report.admin_id == current_user.id).offset(skip).limit(limit).all()

@router.post("/", response_model=ReportSchema)
def create_report(report_in: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = Report(**report_in.dict(), admin_id=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
""",
    "notifications.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Notification
from app.schemas.schemas import Notification as NotificationSchema
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[NotificationSchema])
def read_notifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

@router.patch("/{notification_id}/read", response_model=NotificationSchema)
def read_notification(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif
""",
    "messages.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import or_

from app.db.database import get_db
from app.models.models import User, Message
from app.schemas.schemas import Message as MessageSchema, MessageCreate
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MessageSchema])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Message).filter(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=MessageSchema)
def create_message(msg_in: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = Message(**msg_in.dict(), sender_id=current_user.id)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
""",
    "audit_logs.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, AuditLog
from app.schemas.schemas import AuditLog as AuditLogSchema
from app.core.dependencies import get_current_user, RoleChecker

router = APIRouter()

@router.get("/", response_model=List[AuditLogSchema])
def read_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
""",
    "search.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.models.models import User, Candidate, Worker, Partner
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/")
def global_search(q: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Very basic search implementation
    search_term = f"%{q}%"
    
    candidates = db.query(Candidate).filter(
        (Candidate.first_name.ilike(search_term)) | 
        (Candidate.email.ilike(search_term)) | 
        (Candidate.telegram.ilike(search_term))
    ).all()
    
    partners = db.query(Partner).filter(Partner.company_name.ilike(search_term)).all()
    
    # Needs proper RBAC filtering based on current_user role
    return {
        "candidates": [{"id": c.id, "name": c.first_name, "type": "Candidate"} for c in candidates],
        "partners": [{"id": p.id, "name": p.company_name, "type": "Partner"} for p in partners]
    }
"""
}

for filename, content in files.items():
    with open(os.path.join(base_dir, filename), "w") as f:
        f.write(content)

print("Generated remaining APIs")
