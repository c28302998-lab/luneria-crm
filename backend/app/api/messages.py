from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import or_

from app.db.database import get_db
from app.models.models import User, Message
from app.schemas.schemas import Message as MessageSchema, MessageCreate
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MessageSchema])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Message).filter(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=MessageSchema)
def create_message(msg_in: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = Message(**msg_in.dict(), sender_id=current_user.id)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@router.patch("/mark-read/{sender_id}")
def mark_messages_read(sender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.sender_id == sender_id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"status": "ok"}
