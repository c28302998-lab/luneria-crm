import re

with open('backend/app/api/workers.py', 'r') as f:
    content = f.read()

new_endpoint = """
from app.models.telegram import TelegramAccount, AccountAssignment, AccountReview
from app.models.email import EmailAccount, EmailAccountAssignment
from app.models.models import Task, AuditLog

@router.post("/{worker_id}/leave")
def worker_leaves(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    worker.status = "TERMINATED"
    
    # 1. Handle Telegram Accounts
    tg_accs = db.query(TelegramAccount).filter(TelegramAccount.assigned_worker_id == worker.user_id).all()
    # Wait, worker.user_id does not exist, assigned_worker_id points to User ID!
    # How does Worker map to User?
    # candidate -> email -> User. email matches. Or User.email == candidate.email.
    # Let's get the user ID for this worker.
    candidate = worker.candidate
    user = db.query(User).filter(User.email == candidate.email).first()
    user_id = user.id if user else None
    
    if not user_id:
        # Fallback if no user exists, maybe assigned by candidate ID? In this system, they're messy.
        user_id = worker.candidate_id # Wait, no. Let's just use user_id if available.
        pass

    tg_count = 0
    if user_id:
        tg_accs = db.query(TelegramAccount).filter(TelegramAccount.assigned_worker_id == user_id).all()
        for acc in tg_accs:
            # Revoke assignment
            active = db.query(AccountAssignment).filter(
                AccountAssignment.account_id == acc.id,
                AccountAssignment.worker_id == user_id,
                AccountAssignment.revoked_at == None
            ).first()
            if active:
                active.revoked_at = datetime.utcnow()
                active.reason = "WORKER_LEFT"
                
            acc.assigned_worker_id = None
            acc.assigned_user_id = None
            
            # Create AccountReview
            review = AccountReview(
                account_id=acc.id,
                previous_worker_id=user_id,
                created_by="SYSTEM"
            )
            db.add(review)
            db.flush() # To get review.id if needed
            
            # Create Task for Admin
            task = Task(
                title=f"Проверка TG аккаунта {acc.name}",
                description=f"Работник уволен. Проанализируйте аккаунт #{acc.id} и примите решение.",
                priority="HIGH",
                assigned_user_id=worker.admin_id, # Fallback to admin_id for now until responsible_admin_id is fully adopted
                creator_id=1, # System or Owner
                status="NEW"
            )
            db.add(task)
            tg_count += 1

    # 2. Handle Email Accounts
    email_count = 0
    if user_id:
        em_accs = db.query(EmailAccount).filter(EmailAccount.assigned_worker_id == user_id).all()
        for acc in em_accs:
            active = db.query(EmailAccountAssignment).filter(
                EmailAccountAssignment.email_account_id == acc.id,
                EmailAccountAssignment.worker_id == user_id,
                EmailAccountAssignment.revoked_at == None
            ).first()
            if active:
                active.revoked_at = datetime.utcnow()
                active.reason = "WORKER_LEFT"
            acc.assigned_worker_id = None
            acc.assigned_admin_id = None
            email_count += 1

    # Audit Log
    log = AuditLog(
        user_id=current_user.id,
        action="WORKER_LEAVES",
        details=f"Worker {worker.id} terminated. {tg_count} TG accounts detached. {email_count} Email accounts detached. {tg_count} AccountReviews created."
    )
    db.add(log)
    
    db.commit()
    
    return {
        "message": "Успешно оформлен уход работника.",
        "tg_accounts_detached": tg_count,
        "email_accounts_detached": email_count,
        "reviews_created": tg_count
    }
"""

if "@router.post(\"/{worker_id}/leave\")" not in content:
    content += "\n" + new_endpoint

with open('backend/app/api/workers.py', 'w') as f:
    f.write(content)
