with open("backend/app/api/workers.py", "r") as f:
    content = f.read()

import re

old_delete = """@router.delete("/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    worker.is_deleted = True
    import datetime
    worker.deleted_at = datetime.datetime.utcnow()
    log_audit(db, current_user.id, "DELETE", "Worker", worker_id, {})
    db.commit()
    return {"status": "success"}"""

new_delete = """@router.delete("/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    worker.is_deleted = True
    import datetime
    worker.deleted_at = datetime.datetime.utcnow()
    
    # Also delete the associated User account so they don't show up in dropdowns and can't log in
    if worker.candidate and worker.candidate.email:
        from app.models.models import User
        user_record = db.query(User).filter(User.email == worker.candidate.email).first()
        if user_record:
            user_record.is_deleted = True
            
    log_audit(db, current_user.id, "DELETE", "Worker", worker_id, {})
    db.commit()
    return {"status": "success"}"""

content = content.replace(old_delete, new_delete)

with open("backend/app/api/workers.py", "w") as f:
    f.write(content)
