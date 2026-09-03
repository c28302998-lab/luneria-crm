from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.models import Account, User, Worker, AccountEmail
from app.schemas.schemas import AccountCreate, AccountUpdate, AccountResponse, AccountEmailCreate, AccountEmailResponse
from app.core.dependencies import get_current_user, RoleChecker
from sqlalchemy import desc

router = APIRouter()

@router.post("/", response_model=AccountResponse)
def create_account(acc_in: AccountCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    acc = Account(
        login=acc_in.login,
        account_number=acc_in.account_number,
        worker_id=acc_in.worker_id,
        partner_id=acc_in.partner_id,
        status=acc_in.status,
        issued_at=datetime.utcnow() if acc_in.status == "ISSUED" else None
    )
    if current_user.role == "OWNER" and hasattr(acc_in, "gmail_address"):
        acc.gmail_address = acc_in.gmail_address
        acc.gmail_password = acc_in.gmail_password
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc

@router.get("/", response_model=List[AccountResponse])
def get_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Account).filter(Account.is_deleted == False).order_by(desc(Account.created_at))
    
    if current_user.role == "ADMIN":
        # Admins only see accounts assigned to their workers
        workers = db.query(Worker).filter(Worker.admin_id == current_user.id).all()
        worker_ids = [w.id for w in workers]
        query = query.filter(Account.worker_id.in_(worker_ids))
        
    return query.all()

@router.patch("/{acc_id:int}", response_model=AccountResponse)
def update_account(acc_id: int, update: AccountUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = db.query(Account).filter(Account.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
        
    # Check permissions
    if current_user.role == "ADMIN":
        # Admins can only change status to "ISSUE" or "NEEDS_REPLACEMENT" for their own accounts
        workers = db.query(Worker).filter(Worker.admin_id == current_user.id).all()
        worker_ids = [w.id for w in workers]
        if acc.worker_id not in worker_ids:
            raise HTTPException(status_code=403, detail="Not your account")
        if update.status and update.status not in ["ISSUE", "NEEDS_REPLACEMENT", "RECEIVED"]:
            raise HTTPException(status_code=403, detail="Admins can only report issues or request replacements")
        
        if update.status:
            acc.status = update.status
    else:
        # Owner / Curator can do anything
        if update.login is not None:
            acc.login = update.login
        if update.account_number is not None:
            acc.account_number = update.account_number
        if update.worker_id is not None:
            acc.worker_id = update.worker_id
        if update.partner_id is not None:
            acc.partner_id = update.partner_id
        if update.status is not None:
            if acc.status != "ISSUED" and update.status == "ISSUED":
                acc.issued_at = datetime.utcnow()
            acc.status = update.status

    db.commit()
    db.refresh(acc)
    return acc

@router.delete("/{acc_id:int}")
def delete_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    acc = db.query(Account).filter(Account.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
        
    acc.is_deleted = True
    db.commit()
    return {"message": "Deleted"}



from sqlalchemy import text


@router.get("/emails", response_model=List[AccountEmailResponse])
def get_emails(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    return db.query(AccountEmail).filter(AccountEmail.is_deleted == False).order_by(desc(AccountEmail.created_at)).all()


@router.post("/emails", response_model=AccountEmailResponse)
def create_email(email_in: AccountEmailCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    email = AccountEmail(email=email_in.email, account_id=email_in.account_id, linked_account_name=email_in.linked_account_name)
    db.add(email)
    db.commit()
    db.refresh(email)
    return email

@router.delete("/emails/{email_id}")
def delete_email(email_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    email = db.query(AccountEmail).filter(AccountEmail.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.is_deleted = True
    db.commit()
    return {"message": "Deleted"}
