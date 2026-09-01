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

async def get_worker_account(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in ["ADMIN", "WORKER", "OWNER"]:
        raise HTTPException(status_code=403, detail="Role not allowed")
        
    worker = db.query(Worker).filter(Worker.user_id == user.id).first()
    if not worker:
        # For testing, if OWNER doesn't have a worker profile, maybe we let them pass? 
        # But policy says "assigned worker". Let's strictly require it.
        raise HTTPException(status_code=403, detail="No worker profile found")
        
    acc = db.query(TelegramAccount).filter(TelegramAccount.assigned_worker_id == worker.id, TelegramAccount.status == TelegramAccountStatus.ACTIVE).first()
    if not acc:
        raise HTTPException(status_code=404, detail="No active Telegram account assigned")
        
    return acc

@router.get("/chats")
async def get_chats(request: Request, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_worker_account), user: User = Depends(get_current_user)):
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
        
        chats = []
        for d in dialogs:
            chats.append({
                "id": str(d.id),
                "name": d.name,
                "is_user": d.is_user,
                "is_group": d.is_group,
                "is_channel": d.is_channel,
                "unread_count": d.unread_count,
                "message": d.message.text if d.message else "",
                "date": d.date.isoformat() if d.date else None
            })
            
        return chats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/messages/{chat_id}")
async def get_messages(chat_id: str, request: Request, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_worker_account), user: User = Depends(get_current_user)):
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
async def send_message(req: SendMessageRequest, request: Request, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_worker_account), user: User = Depends(get_current_user)):
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

