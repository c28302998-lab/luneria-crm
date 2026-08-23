from fastapi import APIRouter, Depends, HTTPException
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
