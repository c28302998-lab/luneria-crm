import re

with open("backend/app/api/shift_reports.py", "r") as f:
    content = f.read()

old_get = """def get_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "WORKER":
        return db.query(ShiftReport).filter(ShiftReport.worker_id == current_user.id, ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    elif current_user.role == "OWNER" or current_user.role == "FINANCE":
        return db.query(ShiftReport).filter(ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    elif current_user.role == "ADMIN":
        from app.models.models import Worker, Candidate
        admin_workers = db.query(Worker).filter(Worker.admin_id == current_user.id).all()
        candidate_ids = [w.candidate_id for w in admin_workers]
        candidate_emails = [c.email for c in db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all() if c.email]
        user_ids = [u.id for u in db.query(User).filter(User.email.in_(candidate_emails)).all()]
        return db.query(ShiftReport).filter(ShiftReport.worker_id.in_(user_ids), ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    else:
        raise HTTPException(status_code=403, detail="Not allowed")"""

new_get = """def get_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "WORKER":
        reports = db.query(ShiftReport).filter(ShiftReport.worker_id == current_user.id, ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    elif current_user.role == "OWNER" or current_user.role == "FINANCE":
        reports = db.query(ShiftReport).filter(ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    elif current_user.role == "ADMIN":
        from app.models.models import Worker, Candidate
        admin_workers = db.query(Worker).filter(Worker.admin_id == current_user.id).all()
        candidate_ids = [w.candidate_id for w in admin_workers]
        candidate_emails = [c.email for c in db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all() if c.email]
        user_ids = [u.id for u in db.query(User).filter(User.email.in_(candidate_emails)).all()]
        reports = db.query(ShiftReport).filter(ShiftReport.worker_id.in_(user_ids), ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()
    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Enrich with worker and admin names
    from app.models.models import Candidate, Worker
    
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
        
    return result"""

content = content.replace(old_get, new_get)

with open("backend/app/api/shift_reports.py", "w") as f:
    f.write(content)
