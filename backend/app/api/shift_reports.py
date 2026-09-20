from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.google_sheets import set_shift_date_for_accounts
from app.models.models import Notification, User, ShiftReport
from app.schemas.schemas import ShiftReportCreate, ShiftReportResponse

from pydantic import BaseModel

class ShiftApproveRequest(BaseModel):
    worker_amount: float
    admin_amount: float

from app.core.dependencies import get_current_user, RoleChecker

router = APIRouter()

@router.post("/", response_model=ShiftReportResponse)
def create_report(report_in: ShiftReportCreate, bg_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "WORKER":
        raise HTTPException(status_code=403, detail="Only workers can submit shift reports")
    
    new_report = ShiftReport(
        worker_id=current_user.id,
        amount=report_in.amount,
        files=report_in.files,
        status="PENDING"
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # Try to find telegram accounts assigned to this worker and update their shift date in sheets
    try:
        from app.models.telegram import TelegramAccount
        import datetime
        accs = db.query(TelegramAccount).filter(TelegramAccount.assigned_worker_id == current_user.id).all()
        acc_ids = [a.id for a in accs]
        if acc_ids:
            now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            bg_tasks.add_task(set_shift_date_for_accounts, acc_ids, now_str)
    except Exception as e:
        print(f"Failed to schedule shift date update: {e}")
        
    # Send notification to Admin
    from app.models.models import Candidate, Worker
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if candidate:
        worker_record = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
        if worker_record and worker_record.admin_id:
            notif = Notification(
                user_id=worker_record.admin_id,
                type="Новый отчет",
                message=f"Работник {candidate.first_name} сдал отчет на сумму ${report_in.amount}."
            )
            db.add(notif)
            db.commit()
            
    return new_report

@router.get("/", response_model=List[ShiftReportResponse])
def get_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "WORKER":
        reports = db.query(ShiftReport).filter(ShiftReport.worker_id == current_user.id, ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    elif current_user.role == "OWNER" or current_user.role == "FINANCE":
        reports = db.query(ShiftReport).filter(ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    elif current_user.role == "ADMIN":
        from app.models.models import Notification, Worker, Candidate
        admin_workers = db.query(Worker).filter(Worker.admin_id == current_user.id).all()
        candidate_ids = [w.candidate_id for w in admin_workers]
        candidate_emails = [c.email for c in db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all() if c.email]
        user_ids = [u.id for u in db.query(User).filter(User.email.in_(candidate_emails)).all()]
        reports = db.query(ShiftReport).filter(ShiftReport.worker_id.in_(user_ids), ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Enrich with worker and admin names
    from app.models.models import Notification, Candidate, Worker
    
    # Pre-fetch all users to avoid N+1 queries
    all_users = {u.id: u for u in db.query(User).all()}
    
    result = []
    for r in reports:
        r_dict = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        worker_user = all_users.get(r.worker_id)
        if worker_user:
            r_dict["worker_name"] = worker_user.name
            
            # Find admin name
            candidate = db.query(Candidate).filter(Candidate.email == worker_user.email).first()
            if candidate:
                worker_record = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
                if worker_record and worker_record.admin_id:
                    admin_user = all_users.get(worker_record.admin_id)
                    if admin_user:
                        r_dict["admin_name"] = admin_user.name
        
        result.append(r_dict)
        
    return result

@router.put("/{report_id}/approve")
def approve_report(report_id: int, payload: ShiftApproveRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    report = db.query(ShiftReport).filter(ShiftReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.status == "APPROVED":
        raise HTTPException(status_code=400, detail="Already approved")
        
    report.status = "APPROVED"
    
    # Save amounts to report
    report.worker_amount = payload.worker_amount
    report.admin_amount = payload.admin_amount
    
    # Add money to worker
    from app.models.models import Notification, Candidate, Worker
    worker_user = db.query(User).filter(User.id == report.worker_id).first()
    if worker_user:
        worker_user.balance = (worker_user.balance or 0.0) + payload.worker_amount
        
        # Find the worker's admin
        candidate = db.query(Candidate).filter(Candidate.email == worker_user.email).first()
        if candidate:
            worker_record = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
            if worker_record and worker_record.admin_id:
                admin_user = db.query(User).filter(User.id == worker_record.admin_id).first()
                if admin_user:
                    admin_user.balance = (admin_user.balance or 0.0) + payload.admin_amount
        
    db.commit()
    return {"ok": True}

@router.delete("/{report_id}")
def delete_shift_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    report = db.query(ShiftReport).filter(ShiftReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if report.status == "APPROVED":
        # Deduct money from worker and admin
        from app.models.models import Notification, Candidate, Worker
        worker_user = db.query(User).filter(User.id == report.worker_id).first()
        if worker_user and report.worker_amount:
            worker_user.balance = (worker_user.balance or 0.0) - report.worker_amount
            
            candidate = db.query(Candidate).filter(Candidate.email == worker_user.email).first()
            if candidate:
                worker_record = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
                if worker_record and worker_record.admin_id and report.admin_amount:
                    admin_user = db.query(User).filter(User.id == worker_record.admin_id).first()
                    if admin_user:
                        admin_user.balance = (admin_user.balance or 0.0) - report.admin_amount
                        
    report.is_deleted = True
    db.commit()
    return {"message": "Deleted"}
