import re

with open('backend/app/api/telegram_admin.py', 'r') as f:
    content = f.read()

# Make sure we import AccountAssignment
if "from app.models.telegram import" in content:
    content = content.replace("from app.models.telegram import", "from app.models.telegram import AccountAssignment,")
else:
    content = content.replace("from app.models.models import", "from app.models.telegram import AccountAssignment\nfrom app.models.models import")

old_code = """        old_user = acc.assigned_user_id
        if current_user.role == "OWNER":
            acc.assigned_user_id = req.user_id
        
        acc.assigned_worker_id = req.worker_id
        if req.worker_note is not None:
            acc.worker_note = req.worker_note
            
        db.commit()"""

new_code = """        old_user = acc.assigned_user_id
        
        # --- NEW HISTORY LOGIC ---
        from datetime import datetime
        active_assignment = db.query(AccountAssignment).filter(
            AccountAssignment.account_id == acc.id,
            AccountAssignment.revoked_at == None
        ).first()
        
        if active_assignment:
            active_assignment.revoked_at = datetime.utcnow()
            active_assignment.reason = "REASSIGNED"
            
        new_assignment = AccountAssignment(
            account_id=acc.id,
            worker_id=req.worker_id,
            admin_id=req.user_id if current_user.role == "OWNER" else acc.assigned_user_id,
            assigned_at=datetime.utcnow()
        )
        db.add(new_assignment)
        # -------------------------

        if current_user.role == "OWNER":
            acc.assigned_user_id = req.user_id
        
        acc.assigned_worker_id = req.worker_id
        if req.worker_note is not None:
            acc.worker_note = req.worker_note
            
        db.commit()"""

content = content.replace(old_code, new_code)

with open('backend/app/api/telegram_admin.py', 'w') as f:
    f.write(content)
