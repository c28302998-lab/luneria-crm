from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.concurrency import run_in_threadpool

from app.db.database import get_db
from app.models.models import User
from app.models.email import EmailAccountAssignment, EmailAccount
from app.schemas.email import EmailAccountCreate, EmailAccountUpdate, EmailAccountResponse, EmailMessageList, EmailMessageDetail, EmailSendRequest
from app.core.dependencies import get_current_user, RoleChecker

import imap_tools
import aiosmtplib
from email.message import EmailMessage
import datetime

router = APIRouter()

@router.post("/accounts", response_model=EmailAccountResponse)
def create_email_account(
    account: EmailAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))
):
    # Verify IMAP connection before adding
    try:
        with imap_tools.MailBox(account.imap_server).login(account.email_address, account.app_password):
            pass # Successfully connected
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect to IMAP: {str(e)}")

    db_acc = EmailAccount(**account.dict())
    if current_user.role == "ADMIN":
        db_acc.assigned_admin_id = current_user.id
        
    db.add(db_acc)
    db.commit()
    db.refresh(db_acc)
    return db_acc

@router.get("/accounts", response_model=List[EmailAccountResponse])
def get_email_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(EmailAccount).filter(EmailAccount.is_deleted == False)
    if current_user.role == "ADMIN":
        query = query.filter(EmailAccount.assigned_admin_id == current_user.id)
    elif current_user.role == "WORKER":
        query = query.filter(EmailAccount.assigned_worker_id == current_user.id)
    return query.all()

@router.patch("/accounts/{acc_id}", response_model=EmailAccountResponse)
def update_email_account(
    acc_id: int,
    update_data: EmailAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))
):
    acc = db.query(EmailAccount).filter(EmailAccount.id == acc_id, EmailAccount.is_deleted == False).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
        
    if current_user.role == "ADMIN" and acc.assigned_admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your account")
        
    update_dict = update_data.dict(exclude_unset=True)
    
    # Check if assignment changed
    from datetime import datetime
    old_worker_id = acc.assigned_worker_id
    new_worker_id = update_dict.get('assigned_worker_id', old_worker_id)
    
    if 'assigned_worker_id' in update_dict and old_worker_id != new_worker_id:
        active_assignment = db.query(EmailAccountAssignment).filter(
            EmailAccountAssignment.email_account_id == acc.id,
            EmailAccountAssignment.revoked_at == None
        ).first()
        if active_assignment:
            active_assignment.revoked_at = datetime.utcnow()
            active_assignment.reason = "REASSIGNED"
            
        if new_worker_id is not None:
            new_assignment = EmailAccountAssignment(
                email_account_id=acc.id,
                worker_id=new_worker_id,
                admin_id=update_dict.get('assigned_admin_id', acc.assigned_admin_id),
                assigned_at=datetime.utcnow()
            )
            db.add(new_assignment)
            
    for k, v in update_dict.items():
        setattr(acc, k, v)
        
    db.commit()
    db.refresh(acc)
    return acc

@router.delete("/accounts/{acc_id}")
def delete_email_account(
    acc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))
):
    acc = db.query(EmailAccount).filter(EmailAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404)
    if current_user.role == "ADMIN" and acc.assigned_admin_id != current_user.id:
        raise HTTPException(status_code=403)
    acc.is_deleted = True
    db.commit()
    return {"ok": True}

def fetch_inbox_sync(imap_server, email_addr, password, limit=30):
    msgs = []
    with imap_tools.MailBox(imap_server).login(email_addr, password) as mailbox:
        for msg in mailbox.fetch(limit=limit, reverse=True):
            msgs.append({
                "uid": msg.uid,
                "subject": msg.subject,
                "sender": msg.from_,
                "date": msg.date,
                "is_unseen": not ('\\Seen' in msg.flags)
            })
    return msgs

def fetch_message_sync(imap_server, email_addr, password, uid: str):
    with imap_tools.MailBox(imap_server).login(email_addr, password) as mailbox:
        for msg in mailbox.fetch(imap_tools.AND(uid=uid)):
            return {
                "uid": msg.uid,
                "subject": msg.subject,
                "sender": msg.from_,
                "date": msg.date,
                "is_unseen": not ('\\Seen' in msg.flags),
                "text": msg.text,
                "html": msg.html
            }
    return None

def check_access(db, acc_id, user):
    acc = db.query(EmailAccount).filter(EmailAccount.id == acc_id, EmailAccount.is_deleted == False).first()
    if not acc:
        raise HTTPException(status_code=404)
    if user.role == "WORKER" and acc.assigned_worker_id != user.id:
        raise HTTPException(status_code=403)
    if user.role == "ADMIN" and acc.assigned_admin_id != user.id:
        raise HTTPException(status_code=403)
    return acc

@router.get("/{acc_id}/inbox", response_model=List[EmailMessageList])
async def get_inbox(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = check_access(db, acc_id, current_user)
    try:
        msgs = await run_in_threadpool(fetch_inbox_sync, acc.imap_server, acc.email_address, acc.app_password)
        return msgs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{acc_id}/message/{uid}", response_model=EmailMessageDetail)
async def get_message(acc_id: int, uid: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = check_access(db, acc_id, current_user)
    try:
        msg = await run_in_threadpool(fetch_message_sync, acc.imap_server, acc.email_address, acc.app_password, uid)
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")
        return msg
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{acc_id}/send")
async def send_email(acc_id: int, req: EmailSendRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = check_access(db, acc_id, current_user)
    
    msg = EmailMessage()
    msg["From"] = acc.email_address
    msg["To"] = req.to_email
    msg["Subject"] = req.subject
    msg.set_content(req.body_text)
    if req.body_html:
        msg.add_alternative(req.body_html, subtype='html')

    try:
        await aiosmtplib.send(
            msg,
            hostname=acc.smtp_server,
            port=acc.smtp_port,
            use_tls=True if acc.smtp_port == 465 else False,
            username=acc.email_address,
            password=acc.app_password
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMTP Error: {str(e)}")


@router.get("/accounts/{acc_id}/history")
def get_email_account_history(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    return db.query(EmailAccountAssignment).filter(EmailAccountAssignment.email_account_id == acc_id).order_by(EmailAccountAssignment.assigned_at.desc()).all()
