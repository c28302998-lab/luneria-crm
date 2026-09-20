import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.db.database import SessionLocal
from app.models.models import User
from app.models.telegram import TelegramAccount, AccountAssignment
from app.models.email import EmailAccount, EmailAccountAssignment
from datetime import datetime

db = SessionLocal()

print("Migrating Telegram Accounts...")
tg_accs = db.query(TelegramAccount).filter(TelegramAccount.assigned_worker_id != None).all()
for acc in tg_accs:
    existing = db.query(AccountAssignment).filter(AccountAssignment.account_id == acc.id, AccountAssignment.worker_id == acc.assigned_worker_id, AccountAssignment.revoked_at == None).first()
    if not existing:
        aa = AccountAssignment(
            account_id=acc.id,
            worker_id=acc.assigned_worker_id,
            admin_id=acc.assigned_user_id,
            assigned_at=datetime.utcnow()
        )
        db.add(aa)

print("Migrating Email Accounts...")
em_accs = db.query(EmailAccount).filter(EmailAccount.assigned_worker_id != None).all()
for acc in em_accs:
    existing = db.query(EmailAccountAssignment).filter(EmailAccountAssignment.email_account_id == acc.id, EmailAccountAssignment.worker_id == acc.assigned_worker_id, EmailAccountAssignment.revoked_at == None).first()
    if not existing:
        ea = EmailAccountAssignment(
            email_account_id=acc.id,
            worker_id=acc.assigned_worker_id,
            admin_id=acc.assigned_admin_id,
            assigned_at=datetime.utcnow()
        )
        db.add(ea)

db.commit()
print("Migration completed.")
db.close()
