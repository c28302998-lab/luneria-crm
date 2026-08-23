from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, AuditLog
from app.schemas.schemas import AuditLog as AuditLogSchema
from app.core.dependencies import get_current_user, RoleChecker

router = APIRouter()

@router.get("/", response_model=List[AuditLogSchema])
def read_audit_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "OWNER":
        return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    else:
        return db.query(AuditLog).filter(AuditLog.user_id == current_user.id).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
