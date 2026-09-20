import re

with open('backend/app/api/telegram_admin.py', 'r') as f:
    content = f.read()

old_code = """    acc.assigned_user_id = None
    acc.status = TelegramAccountStatus.DISABLED
    db.commit()"""

new_code = """    from datetime import datetime
    active_assignment = db.query(AccountAssignment).filter(
        AccountAssignment.account_id == acc.id,
        AccountAssignment.revoked_at == None
    ).first()
    
    if active_assignment:
        active_assignment.revoked_at = datetime.utcnow()
        active_assignment.reason = "REVOKED_BY_OWNER"
        
    acc.assigned_user_id = None
    acc.assigned_worker_id = None
    acc.status = TelegramAccountStatus.DISABLED
    db.commit()"""

content = content.replace(old_code, new_code)

with open('backend/app/api/telegram_admin.py', 'w') as f:
    f.write(content)
