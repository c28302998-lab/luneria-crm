from app.core.dependencies import RoleChecker
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.services.google_sheets import sync_account_to_sheets
import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import traceback

from ..db.database import get_db
from ..models.models import User, Account
from ..models.telegram import TelegramAccount, TelegramAccountStatus, TelegramAuditLog
from .auth import get_current_user
from ..services.telegram_manager import telegram_manager

router = APIRouter(prefix="/telegram/admin", tags=["Telegram Admin"])


def get_assigned_email(db: Session, worker_user_id: int) -> str:
    if not worker_user_id:
        return ""
    from ..models.email import EmailAccount
    email_acc = db.query(EmailAccount).filter(EmailAccount.assigned_worker_id == worker_user_id, EmailAccount.is_deleted == False).first()
    if email_acc:
        return email_acc.email_address
    return ""

def get_partner_name(db: Session, worker_user_id: int) -> Optional[str]:
    if not worker_user_id:
        return None
    from ..models.models import User, Worker, Partner
    user = db.query(User).filter(User.id == worker_user_id).first()
    if not user or not user.candidate_id:
        return None
    worker = db.query(Worker).filter(Worker.candidate_id == user.candidate_id).first()
    if not worker or not worker.partner_id:
        return None
    partner = db.query(Partner).filter(Partner.id == worker.partner_id).first()
    if partner:
        return partner.company_name
    return None


def check_owner(user: User = Depends(get_current_user)):
    if user.role != "OWNER":
        raise HTTPException(status_code=403, detail="Only owner can perform this action")
    return user

class SendCodeRequest(BaseModel):
    phone: str

class VerifyCodeRequest(BaseModel):
    phone: str
    code: str
    password: Optional[str] = None
    account_name: str

@router.post("/auth/send-code")
async def send_code(req: SendCodeRequest, current_user: User = Depends(check_owner)):
    try:
        hash_val = await telegram_manager.auth_send_code(req.phone)
        return {"status": "success", "phone_code_hash": hash_val}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/verify-code")
async def verify_code(req: VerifyCodeRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner), bg_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        session_string, username = await telegram_manager.auth_sign_in(req.phone, req.code, req.password)
        
        # Save to DB
        acc = TelegramAccount(
            name=req.account_name,
            phone=req.phone,
            username=username,
            session_string=session_string,
            status=TelegramAccountStatus.ACTIVE,
            two_fa_password=req.password
        )
        db.add(acc)
        db.commit()
        db.refresh(acc)
        
        # Audit Log
        try:
            log = TelegramAuditLog(
            user_id=current_user.id,
            account_id=acc.id,
            action="CONNECT_ACCOUNT",
            details=f"Owner connected new account {req.phone}"
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Failed to save audit log: {e}")
        
        # Google Sheets Sync
        try:
            bg_tasks.add_task(
                sync_account_to_sheets,
                account_id=acc.id,
                account_name=acc.name,
                phone=acc.phone,
                password=acc.two_fa_password,
                worker_name="Свободен",
                admin_name="Без админа",
                start_date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
                action="Добавление аккаунта",
                partner_name=get_partner_name(db, acc.assigned_worker_id),
            email_address=get_assigned_email(db, acc.assigned_worker_id)
            )
        except Exception as e:
            print(f"Error scheduling Sheets sync: {e}")
            
        return {"status": "success", "account_id": acc.id}
        
    except ValueError as e:
        if str(e) == "2FA_REQUIRED":
            return {"status": "2FA_REQUIRED"}
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))

from ..schemas.telegram import TelegramAccountResponse, TelegramAuditLogResponse


@router.post("/accounts/sync-legacy")
def sync_legacy_accounts(db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    tg_accs = db.query(TelegramAccount).filter(TelegramAccount.is_deleted == False).all()
    existing_accs = db.query(Account).filter(Account.is_deleted == False).all()
    existing_phones = {a.account_number for a in existing_accs if a.account_number}
    
    added = 0
    for tg in tg_accs:
        if tg.phone not in existing_phones:
            new_acc = Account(
                login=tg.username if tg.username else tg.name,
                account_number=tg.phone,
                status="FREE"
            )
            db.add(new_acc)
            existing_phones.add(tg.phone)
            added += 1
    
    db.commit()
    return {"status": "ok", "synced": added}


class EditPasswordRequest(BaseModel):
    password: Optional[str] = None

@router.put("/accounts/{acc_id}/2fa-password")
def edit_2fa_password_admin(acc_id: int, req: EditPasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner), bg_tasks: BackgroundTasks = BackgroundTasks()):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    acc.two_fa_password = req.password
    db.commit()
    # Google Sheets Sync
    try:
        w_name = acc.assigned_worker.name if acc.assigned_worker else "Свободен"
        a_name = acc.assigned_user.name if acc.assigned_user else "Без админа"
        bg_tasks.add_task(
            sync_account_to_sheets,
            account_id=acc.id,
            account_name=acc.name,
            phone=acc.phone,
            password=acc.two_fa_password,
            worker_name=w_name,
            admin_name=a_name,
            start_date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            action="Смена пароля 2FA",
            partner_name=get_partner_name(db, acc.assigned_worker_id),
            email_address=get_assigned_email(db, acc.assigned_worker_id)
        )
    except Exception as e:
        print(f"Error scheduling Sheets sync: {e}")
        
    return {"status": "ok"}

@router.get("/accounts", response_model=List[TelegramAccountResponse])
def get_accounts(db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    return db.query(TelegramAccount).filter(TelegramAccount.is_deleted == False).order_by(TelegramAccount.id.asc()).all()

class AssignAccountRequest(BaseModel):
    user_id: Optional[int]
    worker_id: Optional[int] = None
    worker_note: Optional[str] = None

@router.patch("/accounts/{acc_id}/assign")
async def assign_account(acc_id: int, req: AssignAccountRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), bg_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        if current_user.role not in ["OWNER", "ADMIN"]:
            raise HTTPException(status_code=403, detail="Not allowed")
            
        acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")
            
        if current_user.role == "ADMIN" and acc.assigned_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned to you")
            
        old_user = acc.assigned_user_id
        
        # --- NEW HISTORY LOGIC ---
        from datetime import datetime
        active_assignment = db.query(AccountAssignment).filter(
            AccountAssignment.account_id == acc.id,
            AccountAssignment.revoked_at == None
        ).first()
        

        if active_assignment:
            active_assignment.revoked_at = datetime.utcnow()
            active_assignment.reason = "REASSIGNED"
            
        if req.worker_id is None and acc.assigned_worker_id is not None:
            # Create AccountReview if unassigned manually
            from app.models.telegram import AccountReview
            review = AccountReview(
                account_id=acc.id,
                previous_worker_id=acc.assigned_worker_id,
                created_by=f"Admin {current_user.id}"
            )
            db.add(review)
            
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
            
        db.commit()
        db.refresh(acc)
        
        # Audit log
        try:
            log = TelegramAuditLog(
            user_id=current_user.id,
            account_id=acc.id,
            action="ASSIGN_ACCOUNT",
            details=f"Changed assigned worker from {old_user} to {req.user_id}"
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Failed to save audit log: {e}")
        
        # Session Lock: If changing worker, kill active session to prevent old worker from using it
        if old_user != req.user_id:
            await telegram_manager.disconnect_account(acc.id)
            
        # Google Sheets Sync
        try:
            w_name = acc.assigned_worker.name if acc.assigned_worker else "Свободен"
            a_name = acc.assigned_user.name if acc.assigned_user else "Без админа"
            bg_tasks.add_task(
                sync_account_to_sheets,
                account_id=acc.id,
                account_name=acc.name,
                phone=acc.phone,
                password=acc.two_fa_password,
                worker_name=w_name,
                admin_name=a_name,
                start_date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
                action="Передача аккаунта",
                partner_name=get_partner_name(db, acc.assigned_worker_id),
            email_address=get_assigned_email(db, acc.assigned_worker_id)
            )
        except Exception as e:
            print(f"Error scheduling Sheets sync: {e}")
            
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/accounts/{acc_id}/revoke")
async def revoke_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
        
    from datetime import datetime
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
    db.commit()
    
    try:
        log = TelegramAuditLog(
        user_id=current_user.id,
        account_id=acc.id,
        action="REVOKE_ACCOUNT",
        details="Owner revoked access and disabled account"
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save audit log: {e}")
    
    # Session Lock: Kill immediately
    await telegram_manager.disconnect_account(acc.id)
    return {"status": "success"}

@router.get("/audit", response_model=List[TelegramAuditLogResponse])
def get_audit_logs(limit: int = 1000, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    return db.query(TelegramAuditLog).order_by(TelegramAuditLog.created_at.desc()).limit(limit).all()

from app.models.telegram import AccountAssignment, TelegramRequest, TelegramRequestStatus

@router.get("/requests")
def get_requests(db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    return db.query(TelegramRequest).order_by(TelegramRequest.created_at.desc()).all()

class RequestStatusUpdate(BaseModel):
    status: TelegramRequestStatus
    owner_comment: Optional[str] = None

@router.patch("/requests/{req_id}/status")
def update_request_status(req_id: int, update: RequestStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    req = db.query(TelegramRequest).filter(TelegramRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.status = update.status
    req.owner_comment = update.owner_comment
    db.commit()
    
    # Audit
    try:
        log = TelegramAuditLog(
        user_id=current_user.id,
        account_id=req.account_id,
        action="UPDATE_REQUEST",
        details=f"Updated request {req.id} to {update.status.value}"
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save audit log: {e}")
    return {"status": "success"}

class AccountStatusUpdate(BaseModel):
    status: TelegramAccountStatus

@router.patch("/accounts/{acc_id}/status")
async def update_account_status(acc_id: int, update: AccountStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
        
    old_status = acc.status
    acc.status = update.status
    db.commit()
    
    if update.status != TelegramAccountStatus.ACTIVE:
        await telegram_manager.disconnect_account(acc.id)
        
    try:
        log = TelegramAuditLog(
        user_id=current_user.id,
        account_id=acc.id,
        action="UPDATE_STATUS",
        details=f"Changed status from {old_status.value} to {update.status.value}"
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save audit log: {e}")
    return {"status": "success"}

@router.get("/accounts/{acc_id}/stats")
def get_account_stats(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(404)
        
    # Get last IP, OS, Browser
    last_log = db.query(TelegramAuditLog).filter(TelegramAuditLog.account_id == acc_id).order_by(TelegramAuditLog.created_at.desc()).first()
    
    # Is online? (Activity within last 5 minutes)
    import datetime
    is_online = False
    if acc.last_activity_at:
        is_online = (datetime.datetime.utcnow() - acc.last_activity_at).total_seconds() < 300
        
    return {
        "status": acc.status,
        "is_online": is_online,
        "total_messages": acc.total_messages_sent,
        "total_work_seconds": acc.total_work_seconds,
        "last_activity": acc.last_activity_at,
        "last_ip": last_log.ip_address if last_log else None,
        "last_browser": last_log.browser if last_log else None,
        "last_os": last_log.os if last_log else None
    }


class MaskUpdate(BaseModel):
    mask_client_names: bool

@router.patch("/accounts/{acc_id}/mask")
def update_account_mask(acc_id: int, update: MaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(404)
    acc.mask_client_names = update.mask_client_names
    db.commit()
    return {"status": "success"}

class AliasCreate(BaseModel):
    tg_chat_id: str
    custom_name: str

from app.models.telegram import AccountAssignment, TelegramChatAlias

@router.post("/accounts/{acc_id}/aliases")
def set_chat_alias(acc_id: int, req: AliasCreate, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    alias = db.query(TelegramChatAlias).filter(TelegramChatAlias.account_id == acc_id, TelegramChatAlias.tg_chat_id == req.tg_chat_id).first()
    if alias:
        alias.custom_name = req.custom_name
    else:
        alias = TelegramChatAlias(account_id=acc_id, tg_chat_id=req.tg_chat_id, custom_name=req.custom_name)
        db.add(alias)
    db.commit()
    return {"status": "success"}

@router.delete("/accounts/{acc_id}")
def delete_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner), bg_tasks: BackgroundTasks = BackgroundTasks()):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # We soft delete it
    acc.is_deleted = True
    db.commit()
    # Google Sheets Sync
    try:
        bg_tasks.add_task(
            sync_account_to_sheets,
            account_id=acc.id,
            account_name=acc.name,
            phone=acc.phone,
            password="",
            worker_name="",
            admin_name="",
            start_date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            action="Удаление аккаунта",
            partner_name=get_partner_name(db, acc.assigned_worker_id),
            email_address=get_assigned_email(db, acc.assigned_worker_id)
        )
    except Exception as e:
        print(f"Error scheduling Sheets sync: {e}")
        
    return {"status": "ok"}

class UpdateChecklistRequest(BaseModel):
    setup_checklist: Optional[str]

@router.patch("/accounts/{acc_id}/checklist")
def update_checklist(acc_id: int, req: UpdateChecklistRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    acc.setup_checklist = req.setup_checklist
    db.commit()
    return {"status": "ok"}

@router.post("/accounts/{acc_id}/approve-issue")
def approve_issue(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    acc.issue_request_status = 'APPROVED'
    db.commit()
    return {"status": "ok"}

@router.post("/accounts/{acc_id}/sync")
async def sync_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        client = await telegram_manager.get_client(acc.id, acc.session_string)
        me = await client.get_me()
        if me:
            acc.name = f"{me.first_name or ''} {me.last_name or ''}".strip() or "No Name"
            acc.username = me.username
            acc.phone = me.phone
            db.commit()
            return {"status": "success", "username": acc.username, "name": acc.name, "phone": acc.phone}
        return {"status": "error", "detail": "Could not get user info"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts/{acc_id}/history")
def get_account_history(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    return db.query(AccountAssignment).filter(AccountAssignment.account_id == acc_id).order_by(AccountAssignment.assigned_at.desc()).all()
