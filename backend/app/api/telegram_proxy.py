from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeAudio, DocumentAttributeVideo
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
    if user.role in ["WORKER", "CANDIDATE"]:
        query = query.filter(TelegramAccount.assigned_worker_id == user.id)
    elif user.role == "ADMIN":
        query = query.filter(TelegramAccount.assigned_user_id == user.id)
    accs = query.all()
    return [{"id": a.id, "name": a.name, "phone": a.phone, "username": a.username, "setup_checklist": a.setup_checklist, "issue_request_status": a.issue_request_status, "two_fa_password": a.two_fa_password if a.issue_request_status == "APPROVED" else None} for a in accs]


async def get_user_account(account_id: Optional[int] = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(TelegramAccount).filter(TelegramAccount.is_deleted == False)
    if user.role in ["WORKER", "CANDIDATE"]:
        query = query.filter(TelegramAccount.assigned_worker_id == user.id)
    elif user.role == "ADMIN":
        query = query.filter(TelegramAccount.assigned_user_id == user.id)
    if account_id:
        query = query.filter(TelegramAccount.id == account_id)
    acc = query.first()
    if not acc:
        raise HTTPException(status_code=404, detail="No active Telegram account assigned")
    return acc

from fastapi import Response

@router.get("/accounts/{account_id}/chats/{chat_id}/messages/{message_id}/media")
async def get_message_media(account_id: int, chat_id: str, message_id: int, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = await get_user_account(account_id, user, db)
    
    try:
        peer_id = int(chat_id)
    except:
        peer_id = chat_id
        
    try:
        data = await telegram_manager.download_message_media(acc.id, peer_id, message_id, acc.session_string)
        if not data:
            raise HTTPException(status_code=404, detail="Media not found or could not be downloaded")
        
        # We can guess content type based on URL parameter ?type=voice
        mt = "application/octet-stream"
        if request.query_params.get("type") == "voice":
            mt = "audio/ogg"
        elif request.query_params.get("type") == "photo":
            mt = "image/jpeg"
            
        return Response(content=data, media_type=mt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        me = await client.get_me()
        for d in dialogs:
            chat_id_str = str(d.id)
            chat_name = d.name
            
            if d.entity and d.entity.id == me.id:
                chat_name = "Избранное"
            
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
                "original_name": d.name if user.role == "OWNER" else None,
                "archived": getattr(d, 'archived', False)
            })
            
        return chats
    except Exception as e:
        # Automations: Detect FloodWait
        if "FloodWaitError" in type(e).__name__ or "flood wait" in str(e).lower():
            from app.models.models import Task, User
            admin_id = acc.responsible_admin_id or acc.assigned_user_id
            if not admin_id:
                owner = db.query(User).filter(User.role == "OWNER").first()
                admin_id = owner.id if owner else 1
            task = Task(
                title=f"Автоматизация: FloodWait на аккаунте {acc.name}",
                description=f"Аккаунт получил спам-блок или FloodWait. Ошибка: {str(e)}",
                priority="HIGH",
                assigned_user_id=admin_id,
                creator_id=1,
                status="NEW"
            )
            db.add(task)
            db.commit()
            
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
            
        try:
            msgs = await client.get_messages(peer_id, limit=50)
        except ValueError as e:
            if "entity" in str(e).lower() or "find" in str(e).lower():
                await client.get_dialogs(limit=200)
                msgs = await client.get_messages(peer_id, limit=50)
            else:
                raise e
        
        messages = []
        for m in msgs:
            media_type = None
            if getattr(m, 'media', None):
                if isinstance(m.media, MessageMediaPhoto):
                    media_type = "photo"
                elif isinstance(m.media, MessageMediaDocument):
                    if hasattr(m.media.document, 'attributes'):
                        for attr in m.media.document.attributes:
                            if isinstance(attr, DocumentAttributeAudio):
                                media_type = "voice" if getattr(attr, 'voice', False) else "audio"
                            elif isinstance(attr, DocumentAttributeVideo):
                                media_type = "video"
                    if not media_type:
                        media_type = "document"

            messages.append({
                "id": m.id,
                "sender_id": str(m.sender_id) if m.sender_id else None,
                "text": m.text,
                "date": m.date.isoformat() if m.date else None,
                "is_reply": m.is_reply,
                "out": m.out,
                "media_type": media_type
            })
            
        return messages
    except Exception as e:
        # Automations: Detect FloodWait
        if "FloodWaitError" in type(e).__name__ or "flood wait" in str(e).lower():
            from app.models.models import Task, User
            admin_id = acc.responsible_admin_id or acc.assigned_user_id
            if not admin_id:
                owner = db.query(User).filter(User.role == "OWNER").first()
                admin_id = owner.id if owner else 1
            task = Task(
                title=f"Автоматизация: FloodWait на аккаунте {acc.name}",
                description=f"Аккаунт получил спам-блок или FloodWait. Ошибка: {str(e)}",
                priority="HIGH",
                assigned_user_id=admin_id,
                creator_id=1,
                status="NEW"
            )
            db.add(task)
            db.commit()
            
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
            
        try:
            sent = await client.send_message(peer_id, req.text)
        except ValueError as e:
            if "entity" in str(e).lower() or "find" in str(e).lower():
                # Cache missing on this worker. Fetch dialogs to populate cache.
                await client.get_dialogs(limit=200)
                sent = await client.send_message(peer_id, req.text)
            else:
                raise e
        
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
        # Automations: Detect FloodWait
        if "FloodWaitError" in type(e).__name__ or "flood wait" in str(e).lower():
            from app.models.models import Task, User
            admin_id = acc.responsible_admin_id or acc.assigned_user_id
            if not admin_id:
                owner = db.query(User).filter(User.role == "OWNER").first()
                admin_id = owner.id if owner else 1
            task = Task(
                title=f"Автоматизация: FloodWait на аккаунте {acc.name}",
                description=f"Аккаунт получил спам-блок или FloodWait. Ошибка: {str(e)}",
                priority="HIGH",
                assigned_user_id=admin_id,
                creator_id=1,
                status="NEW"
            )
            db.add(task)
            db.commit()
            
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

@router.get("/resolve")
async def resolve_entity(query: str, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_user_account), user: User = Depends(get_current_user)):
    try:
        chat = await telegram_manager.resolve_entity(acc.id, query, acc.session_string)
        return chat
    except Exception as e:
        # Automations: Detect FloodWait
        if "FloodWaitError" in type(e).__name__ or "flood wait" in str(e).lower():
            from app.models.models import Task, User
            admin_id = acc.responsible_admin_id or acc.assigned_user_id
            if not admin_id:
                owner = db.query(User).filter(User.role == "OWNER").first()
                admin_id = owner.id if owner else 1
            task = Task(
                title=f"Автоматизация: FloodWait на аккаунте {acc.name}",
                description=f"Аккаунт получил спам-блок или FloodWait. Ошибка: {str(e)}",
                priority="HIGH",
                assigned_user_id=admin_id,
                creator_id=1,
                status="NEW"
            )
            db.add(task)
            db.commit()
            
        raise HTTPException(status_code=400, detail=str(e))


import os
import hashlib

@router.get("/accounts/{account_id}/avatar/{entity_id}")
async def get_avatar(account_id: int, entity_id: int, db: Session = Depends(get_db)):
    try:
        cache_dir = "uploads/avatars"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{account_id}_{entity_id}.jpg")
        
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                data = f.read()
            if not data:
                return {"error": "No avatar"}
        else:
            acc = db.query(TelegramAccount).get(account_id)
            if not acc: return {"error": "No avatar"}
            data = await telegram_manager.get_profile_photo(account_id, entity_id, acc.session_string)
            with open(cache_path, "wb") as f:
                f.write(data if data else b"")
                
        if data:
            from fastapi.responses import Response
            return Response(content=data, media_type="image/jpeg")
        return {"error": "No avatar"}
    except Exception as e:
        # Automations: Detect FloodWait
        if "FloodWaitError" in type(e).__name__ or "flood wait" in str(e).lower():
            from app.models.models import Task, User
            admin_id = acc.responsible_admin_id or acc.assigned_user_id
            if not admin_id:
                owner = db.query(User).filter(User.role == "OWNER").first()
                admin_id = owner.id if owner else 1
            task = Task(
                title=f"Автоматизация: FloodWait на аккаунте {acc.name}",
                description=f"Аккаунт получил спам-блок или FloodWait. Ошибка: {str(e)}",
                priority="HIGH",
                assigned_user_id=admin_id,
                creator_id=1,
                status="NEW"
            )
            db.add(task)
            db.commit()
            
        raise HTTPException(status_code=400, detail=str(e))

