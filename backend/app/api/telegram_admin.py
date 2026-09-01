from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import traceback

from ..db.database import get_db
from ..models.models import User
from ..models.telegram import TelegramAccount, TelegramAccountStatus, TelegramAuditLog
from .auth import get_current_user
from ..services.telegram_manager import telegram_manager

router = APIRouter(prefix="/telegram/admin", tags=["Telegram Admin"])

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
async def verify_code(req: VerifyCodeRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    try:
        session_string = await telegram_manager.auth_sign_in(req.phone, req.code, req.password)
        
        # Save to DB
        acc = TelegramAccount(
            name=req.account_name,
            phone=req.phone,
            session_string=session_string,
            status=TelegramAccountStatus.ACTIVE
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
        
        return {"status": "success", "account_id": acc.id}
        
    except ValueError as e:
        if str(e) == "2FA_REQUIRED":
            return {"status": "2FA_REQUIRED"}
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))

from ..schemas.telegram import TelegramAccountResponse, TelegramAuditLogResponse

@router.get("/accounts", response_model=List[TelegramAccountResponse])
def get_accounts(db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    return db.query(TelegramAccount).filter(TelegramAccount.is_deleted == False).all()

class AssignAccountRequest(BaseModel):
    user_id: Optional[int]

@router.patch("/accounts/{acc_id}/assign")
async def assign_account(acc_id: int, req: AssignAccountRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    try:
        acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")
            
        old_user = acc.assigned_user_id
        acc.assigned_user_id = req.user_id
        db.commit()
        
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
        
    acc.assigned_user_id = None
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
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    return db.query(TelegramAuditLog).order_by(TelegramAuditLog.created_at.desc()).limit(limit).all()

from app.models.telegram import TelegramRequest, TelegramRequestStatus

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

from app.models.telegram import TelegramChatAlias

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
def delete_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # We soft delete it
    acc.is_deleted = True
    db.commit()
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
