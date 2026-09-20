import re

# 1. telegram_admin.py history
with open('backend/app/api/telegram_admin.py', 'r') as f:
    content = f.read()
    
new_tg_history = """
@router.get("/accounts/{acc_id}/history")
def get_account_history(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    return db.query(AccountAssignment).filter(AccountAssignment.account_id == acc_id).order_by(AccountAssignment.assigned_at.desc()).all()
"""
if "@router.get(\"/accounts/{acc_id}/history\")" not in content:
    content += new_tg_history
    
with open('backend/app/api/telegram_admin.py', 'w') as f:
    f.write(content)

# 2. emails.py history
with open('backend/app/api/emails.py', 'r') as f:
    content = f.read()

new_em_history = """
@router.get("/accounts/{acc_id}/history")
def get_email_account_history(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    return db.query(EmailAccountAssignment).filter(EmailAccountAssignment.email_account_id == acc_id).order_by(EmailAccountAssignment.assigned_at.desc()).all()
"""
if "@router.get(\"/accounts/{acc_id}/history\")" not in content:
    content += new_em_history

with open('backend/app/api/emails.py', 'w') as f:
    f.write(content)

# 3. workers.py history
with open('backend/app/api/workers.py', 'r') as f:
    content = f.read()

new_w_history = """
from app.models.telegram import AccountAssignment
from app.models.email import EmailAccountAssignment
@router.get("/{worker_id}/history")
def get_worker_history(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker: raise HTTPException(status_code=404)
    # We need the user id
    user = None
    if worker.candidate and worker.candidate.email:
        user = db.query(User).filter(User.email == worker.candidate.email).first()
    user_id = user.id if user else worker.candidate_id
    
    tg_hist = db.query(AccountAssignment).filter(AccountAssignment.worker_id == user_id).order_by(AccountAssignment.assigned_at.desc()).all()
    em_hist = db.query(EmailAccountAssignment).filter(EmailAccountAssignment.worker_id == user_id).order_by(EmailAccountAssignment.assigned_at.desc()).all()
    
    return {
        "telegram": tg_hist,
        "email": em_hist
    }
"""
if "@router.get(\"/{worker_id}/history\")" not in content:
    content += new_w_history

with open('backend/app/api/workers.py', 'w') as f:
    f.write(content)
