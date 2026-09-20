from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Report
from app.schemas.schemas import Report as ReportSchema, ReportCreate
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ReportSchema])
def read_reports(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "OWNER":
        return db.query(Report).filter(Report.is_deleted == False).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    else:
        return db.query(Report).filter(Report.admin_id == current_user.id, Report.is_deleted == False).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=ReportSchema)
def create_report(report_in: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = Report(**report_in.dict(), admin_id=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["OWNER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return {"status": "success"}
