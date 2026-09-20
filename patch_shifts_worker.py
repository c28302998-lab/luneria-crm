import re

with open('backend/app/api/shifts.py', 'r') as f:
    content = f.read()

old_code = """    worker = db.query(Worker).filter(Worker.user_id == current_user.id).first()
    admin_id = worker.admin_id if worker else None"""

new_code = """    # Find worker via Candidate email
    from app.models.models import Candidate
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    worker = None
    if candidate:
        worker = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
    admin_id = worker.admin_id if worker else None"""

content = content.replace(old_code, new_code)

with open('backend/app/api/shifts.py', 'w') as f:
    f.write(content)
