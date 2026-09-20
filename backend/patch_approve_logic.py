import re

with open("app/api/shift_reports.py", "r") as f:
    content = f.read()

old_logic = """    # Add money to worker
    worker = db.query(User).filter(User.id == report.worker_id).first()
    if worker:
        worker.balance = (worker.balance or 0.0) + payload.worker_amount
        # Add money to admin (worker.curator_id)
        if worker.curator_id:
            admin = db.query(User).filter(User.id == worker.curator_id).first()
            if admin:
                admin.balance = (admin.balance or 0.0) + payload.admin_amount
        
    db.commit()"""

new_logic = """    # Save amounts to report
    report.worker_amount = payload.worker_amount
    report.admin_amount = payload.admin_amount
    
    # Add money to worker
    from app.models.models import Candidate, Worker
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
        
    db.commit()"""

content = content.replace(old_logic, new_logic)

with open("app/api/shift_reports.py", "w") as f:
    f.write(content)
