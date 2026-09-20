import re

with open('backend/app/api/telegram_admin.py', 'r') as f:
    content = f.read()

# Add a helper function to get email
helper = '''
def get_assigned_email(db: Session, worker_user_id: int) -> str:
    if not worker_user_id:
        return ""
    from ..models.email import EmailAccount
    email_acc = db.query(EmailAccount).filter(EmailAccount.assigned_worker_id == worker_user_id, EmailAccount.is_deleted == False).first()
    if email_acc:
        return email_acc.email_address
    return ""
'''

if 'def get_assigned_email' not in content:
    content = content.replace('def get_partner_name(db: Session, worker_user_id: int) -> Optional[str]:', helper + '\ndef get_partner_name(db: Session, worker_user_id: int) -> Optional[str]:')

# Replace sync calls
content = content.replace(
    'partner_name=get_partner_name(db, acc.assigned_worker_id)',
    'partner_name=get_partner_name(db, acc.assigned_worker_id),\n                email_address=get_assigned_email(db, acc.assigned_worker_id)'
)

# For revoke/change 2fa which has 12 spaces indentation instead of 16
content = content.replace(
    'partner_name=get_partner_name(db, acc.assigned_worker_id),',
    'partner_name=get_partner_name(db, acc.assigned_worker_id),\n            email_address=get_assigned_email(db, acc.assigned_worker_id),'
)
# Fix double commas if any
content = content.replace('email_address=get_assigned_email(db, acc.assigned_worker_id),\n                email_address=get_assigned_email(db, acc.assigned_worker_id)', 'email_address=get_assigned_email(db, acc.assigned_worker_id)')

with open('backend/app/api/telegram_admin.py', 'w') as f:
    f.write(content)
