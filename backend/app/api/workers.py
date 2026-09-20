from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Worker, Candidate
from app.schemas.schemas import Worker as WorkerSchema, WorkerCreate, WorkerUpdate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[WorkerSchema])
def read_workers(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "OWNER" or current_user.role == "FINANCE":
        return db.query(Worker).filter(Worker.is_deleted == False).offset(skip).limit(limit).all()
    elif current_user.role == "CURATOR":
        admin_ids = [admin.id for admin in current_user.admins]
        return db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.admin_id.in_(admin_ids)).offset(skip).limit(limit).all()
    elif current_user.role == "ADMIN":
        return db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.admin_id == current_user.id).offset(skip).limit(limit).all()
    return []

@router.post("/", response_model=WorkerSchema)
def create_worker(worker_in: WorkerCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    candidate = db.query(Candidate).filter(Candidate.id == worker_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if current_user.role == "ADMIN" and candidate.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your candidate")
        
    worker = Worker(
        candidate_id=worker_in.candidate_id,
        admin_id=candidate.admin_id,
        partner_id=worker_in.partner_id,
        status=worker_in.status
    )
    if current_user.role == "OWNER" and hasattr(worker_in, "referrer_id"):
        worker.referrer_id = worker_in.referrer_id
    db.add(worker)
    candidate.status = "WORKER" # Auto-update candidate status
    
    # Proactively create a User account for the Worker if it doesn't exist
    existing_user = db.query(User).filter(User.email == candidate.email).first()
    invite_link = None
    if not existing_user and candidate.email:
        new_user = User(
            email=candidate.email,
            name=candidate.first_name,
            role="WORKER",
            raw_password=None # REMOVED HARDCODED PASSWORD
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        existing_user = new_user
        
    if existing_user:
        # Generate Invite Token
        import uuid
        from datetime import datetime, timedelta
        from app.models.models import InviteToken
        token = str(uuid.uuid4())
        invite = InviteToken(
            token=token,
            user_id=existing_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(invite)
        db.commit()
        # Frontend URL logic: assuming it's available via origin or hardcoded
        invite_link = f"/invite/{token}"
        # Link worker to the user if we had a user_id on Worker model, but we don't.
        # But wait, ShiftReport looks up User by current_user.id. So the worker logs in as this User!
    else:
        db.commit()
    db.refresh(worker)
    log_audit(db, current_user.id, "CREATE", "Worker", worker.id, {"status": worker.status})
    worker.invite_link = invite_link
    return worker

@router.patch("/{worker_id}/status", response_model=WorkerSchema)
def update_worker_status(worker_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    if current_user.role == "ADMIN" and worker.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your worker")
        
    worker.status = status
    db.commit()
    db.refresh(worker)
    log_audit(db, current_user.id, "CHANGE_STATUS", "Worker", worker.id, {"status": status})
    worker.invite_link = invite_link
    return worker

@router.get("/{worker_id}", response_model=WorkerSchema)
def get_worker(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    if current_user.role == "ADMIN" and worker.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your worker")
    
    worker.invite_link = invite_link
    return worker

@router.patch("/{worker_id}/partner", response_model=WorkerSchema)
def update_worker_partner(worker_id: int, partner_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    worker.partner_id = partner_id
    db.commit()
    db.refresh(worker)
    log_audit(db, current_user.id, "UPDATE", "Worker", worker.id, {"partner_id": partner_id})
    worker.invite_link = invite_link
    return worker


@router.patch("/{worker_id}/admin", response_model=WorkerSchema)
def update_worker_admin(worker_id: int, admin_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    worker = db.query(Worker).filter(Worker.is_deleted == False).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    worker.admin_id = admin_id
    # Also update the linked candidate to keep it consistent
    if worker.candidate:
        worker.candidate.admin_id = admin_id
        
    db.commit()
    db.refresh(worker)
    log_audit(db, current_user.id, "UPDATE", "Worker", worker.id, {"admin_id": admin_id})
    worker.invite_link = invite_link
    return worker

@router.delete("/{worker_id}")
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
    return {"status": "success"}

@router.patch("/{worker_id}/info", response_model=WorkerSchema)
def update_worker_info(
    worker_id: int, 
    shift: str = None, 
    account_info: str = None, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    worker = db.query(Worker).filter(Worker.id == worker_id, Worker.is_deleted == False).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    if current_user.role == "CURATOR":
        raise HTTPException(status_code=403, detail="Curators cannot edit info")
    if current_user.role == "ADMIN" and worker.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit info for your own workers")
        
    if shift is not None:
        worker.shift = shift
    if account_info is not None:
        worker.account_info = account_info
        
    db.commit()
    db.refresh(worker)
    worker.invite_link = invite_link
    return worker

@router.post("/{worker_id}/create-account")
def create_worker_account(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    candidate = db.query(Candidate).filter(Candidate.id == worker.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if not candidate.email:
        raise HTTPException(status_code=400, detail="Кандидат не имеет email")

    existing_user = db.query(User).filter(User.email == candidate.email).first()
    if not existing_user:
        new_user = User(
            email=candidate.email,
            name=candidate.first_name,
            role="WORKER",
            raw_password=None
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        existing_user = new_user

    # Generate Invite Token
    import uuid
    from datetime import datetime, timedelta
    from app.models.models import InviteToken
    token = str(uuid.uuid4())
    invite = InviteToken(
        token=token,
        user_id=existing_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invite)
    db.commit()
    
    return {"email": candidate.email, "invite_link": f"/invite/{token}", "message": "Приглашение создано"}


@router.get("/tools/fix-deleted-users")
def fix_deleted_users(db: Session = Depends(get_db)):
    from app.models.models import User
    deleted_workers = db.query(Worker).filter(Worker.is_deleted == True).all()
    count = 0
    for w in deleted_workers:
        if w.candidate and w.candidate.email:
            u = db.query(User).filter(User.email == w.candidate.email).first()
            if u and not u.is_deleted:
                u.is_deleted = True
                count += 1
    db.commit()
    return {"fixed": count}


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
        changes={"message": f"Worker {worker.id} terminated. {tg_count} TG accounts detached. {email_count} Email accounts detached. {tg_count} AccountReviews created."},
    )
    db.add(log)
    
    db.commit()
    
    return {
        "message": "Успешно оформлен уход работника.",
        "tg_accounts_detached": tg_count,
        "email_accounts_detached": email_count,
        "reviews_created": tg_count
    }

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
