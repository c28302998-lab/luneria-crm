from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any
import traceback

from ..db.database import get_db
from ..models.models import User, Worker
from ..models.telegram import TelegramAccount, TelegramAccountStatus, TelegramAuditLog
from .auth import get_current_user
from ..services.telegram_manager import telegram_manager

router = APIRouter(prefix="/telegram/proxy", tags=["Telegram Proxy"])



from typing import Optional

@router.get("/my-accounts")
async def get_my_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(TelegramAccount).filter(TelegramAccount.is_deleted == False).filter(TelegramAccount.status == TelegramAccountStatus.ACTIVE, TelegramAccount.is_deleted == False)
    if user.role != "OWNER":
        query = query.filter(TelegramAccount.assigned_user_id == user.id)
    accs = query.all()
    return [{"id": a.id, "name": a.name, "phone": a.phone, "setup_checklist": a.setup_checklist} for a in accs]


async def get_user_account(account_id: Optional[int] = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(TelegramAccount).filter(TelegramAccount.is_deleted == False)
    if user.role != "OWNER":
        query = query.filter(TelegramAccount.assigned_user_id == user.id)
    if account_id:
        query = query.filter(TelegramAccount.id == account_id)
    acc = query.first()
    if not acc:
        raise HTTPException(status_code=404, detail="No active Telegram account assigned")
    return acc

@router.get("/chats")
async def get_chats(request: Request, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_user_account), user: User = Depends(get_current_user)):
    try:
        client = await telegram_manager.get_client(acc.id, acc.session_string)
        
        # Log opening Telegram
        log = TelegramAuditLog(
            user_id=user.id,
            account_id=acc.id,
            action="FETCH_CHATS",
            ip_address=request.client.host if request.client else None
        )
        db.add(log)
        db.commit()
        
        dialogs = await client.get_dialogs(limit=50)
        
        # Fetch aliases if needed
        aliases = {}
        from app.models.telegram import TelegramChatAlias
        db_aliases = db.query(TelegramChatAlias).filter(TelegramChatAlias.account_id == acc.id).all()
        for a in db_aliases:
            aliases[a.tg_chat_id] = a.custom_name
        
        chats = []
        for d in dialogs:
            chat_id_str = str(d.id)
            chat_name = d.name
            
            is_masked = False
            custom_name = aliases.get(chat_id_str)
            
            if user.role == "OWNER":
                if custom_name:
                    chat_name = f"{d.name} [{custom_name}]"
                else:
                    chat_name = d.name
            else:
                if acc.mask_client_names:
                    is_masked = True
                    chat_name = f"Клиент {str(d.id)[-4:]}"
                else:
                    if custom_name:
                        chat_name = custom_name
                    else:
                        chat_name = d.name

            chats.append({
                "id": chat_id_str,
                "name": chat_name,
                "is_user": d.is_user,
                "is_group": d.is_group,
                "is_channel": d.is_channel,
                "unread_count": d.unread_count,
                "message": d.message.text if d.message else "",
                "date": d.date.isoformat() if d.date else None,
                "is_masked": is_masked,
                "original_name": d.name if user.role == "OWNER" else None
            })
            
        return chats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/messages/{chat_id}")
async def get_messages(chat_id: str, request: Request, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_user_account), user: User = Depends(get_current_user)):
    try:
        client = await telegram_manager.get_client(acc.id, acc.session_string)
        
        # Log opening a specific chat
        log = TelegramAuditLog(
            user_id=user.id,
            account_id=acc.id,
            action="OPEN_CHAT",
            details=f"Opened chat {chat_id}",
            ip_address=request.client.host if request.client else None
        )
        db.add(log)
        db.commit()
        
        # If chat_id is numeric and negative, convert back. Telethon handles int.
        try:
            peer_id = int(chat_id)
        except:
            peer_id = chat_id
            
        msgs = await client.get_messages(peer_id, limit=50)
        
        messages = []
        for m in msgs:
            messages.append({
                "id": m.id,
                "sender_id": str(m.sender_id) if m.sender_id else None,
                "text": m.text,
                "date": m.date.isoformat() if m.date else None,
                "is_reply": m.is_reply,
                "out": m.out
            })
            
        return messages
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class SendMessageRequest(BaseModel):
    chat_id: str
    text: str

@router.post("/send")
async def send_message(req: SendMessageRequest, request: Request, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_user_account), user: User = Depends(get_current_user)):
    try:
        client = await telegram_manager.get_client(acc.id, acc.session_string)
        
        try:
            peer_id = int(req.chat_id)
        except:
            peer_id = req.chat_id
            
        sent = await client.send_message(peer_id, req.text)
        
        # Audit Log
        log = TelegramAuditLog(
            user_id=user.id,
            account_id=acc.id,
            action="SEND_MESSAGE",
            details=f"Sent message to {req.chat_id}: {req.text[:50]}...",
            ip_address=request.client.host if request.client else None
        )
        db.add(log)
        acc.total_messages_sent += 1
        db.commit()
        
        return {"status": "success", "message_id": sent.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from app.schemas.telegram import TelegramRequestCreate, TelegramRequestResponse
from app.models.telegram import TelegramRequest

@router.post("/requests", response_model=TelegramRequestResponse)
def create_request(req: TelegramRequestCreate, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_user_account), user: User = Depends(get_current_user)):
    # Create request
    new_request = TelegramRequest(
        user_id=user.id,
        account_id=acc.id,
        request_type=req.request_type,
        reason=req.reason
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    # Log audit
    log = TelegramAuditLog(
        user_id=user.id,
        account_id=acc.id,
        action="CREATE_REQUEST",
        details=f"Requested {req.request_type}. Reason: {req.reason}"
    )
    db.add(log)
    db.commit()
    
    return new_request

class ProxyAliasCreate(BaseModel):
    custom_name: str

@router.post("/chats/{chat_id}/alias")
def set_proxy_chat_alias(chat_id: str, req: ProxyAliasCreate, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_user_account), user: User = Depends(get_current_user)):
    if user.role != 'OWNER':
        raise HTTPException(status_code=403, detail='Only owner can set aliases')
    from app.models.telegram import TelegramChatAlias
    alias = db.query(TelegramChatAlias).filter(TelegramChatAlias.account_id == acc.id, TelegramChatAlias.tg_chat_id == chat_id).first()
    if alias:
        alias.custom_name = req.custom_name
    else:
        alias = TelegramChatAlias(account_id=acc.id, tg_chat_id=chat_id, custom_name=req.custom_name)
        db.add(alias)
    db.commit()
    return {"status": "success"}

import string
import random

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@router.post("/accounts/{account_id}/request-issue")
async def request_issue(account_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = await get_user_account(account_id, user, db)
    if acc.issue_request_status == 'APPROVED':
        return {"status": "ok"}
    acc.issue_request_status = 'REQUESTED'
    db.commit()
    db.refresh(acc)
    return {"status": "ok", "new_status": acc.issue_request_status}

@router.post("/accounts/{account_id}/finish-issue")
async def finish_issue(account_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = await get_user_account(account_id, user, db)
    if acc.issue_request_status != 'APPROVED':
        raise HTTPException(status_code=400, detail="Not approved for issuance")
        
    old_password = acc.two_fa_password
    new_password = generate_random_password()
    
    try:
        new_session = await telegram_manager.edit_2fa_password(acc.session_string, old_password, new_password)
        acc.two_fa_password = new_password
        acc.session_string = new_session
        acc.issue_request_status = 'NONE'
        db.commit()
        return {"status": "success", "message": "Password rotated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to change 2FA: {str(e)}")
