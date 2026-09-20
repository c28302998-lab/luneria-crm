import re

with open("app/api/shift_reports.py", "r") as f:
    content = f.read()

old_logic = """@router.delete("/{report_id}")
def delete_shift_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    report = db.query(ShiftReport).filter(ShiftReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.is_deleted = True
    db.commit()
    return {"message": "Deleted"}"""

new_logic = """@router.delete("/{report_id}")
def delete_shift_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    report = db.query(ShiftReport).filter(ShiftReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if report.status == "APPROVED":
        # Deduct money from worker and admin
        from app.models.models import Candidate, Worker
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
    return {"message": "Deleted"}"""

content = content.replace(old_logic, new_logic)

with open("app/api/shift_reports.py", "w") as f:
    f.write(content)
