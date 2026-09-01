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
        log = TelegramAuditLog(
            user_id=current_user.id,
            account_id=acc.id,
            action="CONNECT_ACCOUNT",
            details=f"Owner connected new account {req.phone}"
        )
        db.add(log)
        db.commit()
        
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
    worker_id: Optional[int]

@router.patch("/accounts/{acc_id}/assign")
async def assign_account(acc_id: int, req: AssignAccountRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
        
    old_worker = acc.assigned_worker_id
    acc.assigned_worker_id = req.worker_id
    db.commit()
    
    # Audit log
    log = TelegramAuditLog(
        user_id=current_user.id,
        account_id=acc.id,
        action="ASSIGN_ACCOUNT",
        details=f"Changed assigned worker from {old_worker} to {req.worker_id}"
    )
    db.add(log)
    db.commit()
    
    # Session Lock: If changing worker, kill active session to prevent old worker from using it
    if old_worker != req.worker_id:
        await telegram_manager.disconnect_account(acc.id)
        
    return {"status": "success"}

@router.post("/accounts/{acc_id}/revoke")
async def revoke_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
        
    acc.assigned_worker_id = None
    acc.status = TelegramAccountStatus.DISABLED
    db.commit()
    
    log = TelegramAuditLog(
        user_id=current_user.id,
        account_id=acc.id,
        action="REVOKE_ACCOUNT",
        details="Owner revoked access and disabled account"
    )
    db.add(log)
    db.commit()
    
    # Session Lock: Kill immediately
    await telegram_manager.disconnect_account(acc.id)
    return {"status": "success"}

@router.get("/audit", response_model=List[TelegramAuditLogResponse])
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    return db.query(TelegramAuditLog).order_by(TelegramAuditLog.created_at.desc()).limit(limit).all()
