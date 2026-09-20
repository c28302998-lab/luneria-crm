import re

with open('backend/app/api/shifts.py', 'r') as f:
    content = f.read()

# Add BackgroundTasks and set_shift_date_for_accounts to imports
if "from app.services.google_sheets import set_shift_date_for_accounts" not in content:
    content = content.replace("from fastapi import APIRouter, Depends, HTTPException", "from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks")
    content = content.replace("from app.models.models import User, Shift, Worker, Candidate, AuditLog", "from app.models.models import User, Shift, Worker, Candidate, AuditLog\nfrom app.services.google_sheets import set_shift_date_for_accounts")
    content = content.replace("from app.models.telegram import TelegramAccount", "from app.models.telegram import TelegramAccount, AccountAssignment")

# Patch /end
old_end = """@router.post("/end")
def end_shift(req: ShiftEndRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):"""
new_end = """@router.post("/end")
def end_shift(req: ShiftEndRequest, bg_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):"""
content = content.replace(old_end, new_end)

# Inside /end, call bg task
end_logic = """
    active.status = "PENDING_REVIEW"
    
    # Also update google sheets with shift date
    active_assignments = db.query(AccountAssignment).filter(AccountAssignment.worker_id == user_id, AccountAssignment.revoked_at == None).all()
    if active_assignments:
        acc_ids = [a.account_id for a in active_assignments]
        now_str = datetime.utcnow().strftime("%d.%m.%Y")
        bg_tasks.add_task(set_shift_date_for_accounts, acc_ids, now_str)
"""
content = content.replace("active.status = \"PENDING_REVIEW\"", end_logic)

# Patch /approve
old_approve = """@router.post("/{shift_id}/approve")
def approve_shift(shift_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):"""

new_approve = """from pydantic import BaseModel
class ShiftApproveRequest(BaseModel):
    worker_amount: float
    admin_amount: float

@router.post("/{shift_id}/approve")
def approve_shift(shift_id: int, payload: ShiftApproveRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):"""
content = content.replace(old_approve, new_approve)

# Inside approve, add balance
approve_logic = """    shift.status = "APPROVED"
    
    # Add money
    worker_user = None
    worker = db.query(Worker).filter(Worker.id == shift.worker_id).first()
    if worker:
        candidate = db.query(Candidate).filter(Candidate.id == worker.candidate_id).first()
        if candidate and candidate.email:
            worker_user = db.query(User).filter(User.email == candidate.email).first()
            
    if worker_user:
        worker_user.balance = (worker_user.balance or 0.0) + payload.worker_amount
        if worker.admin_id:
            admin_user = db.query(User).filter(User.id == worker.admin_id).first()
            if admin_user:
                admin_user.balance = (admin_user.balance or 0.0) + payload.admin_amount
"""
content = content.replace("    shift.status = \"APPROVED\"", approve_logic)

with open('backend/app/api/shifts.py', 'w') as f:
    f.write(content)
