from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base
from .models import SoftDeleteMixin

class TelegramAccountStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    BLOCKED = "BLOCKED"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"

class TelegramAccount(Base, SoftDeleteMixin):
    __tablename__ = "telegram_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    username = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    session_string = Column(Text, nullable=False) # The Telethon session string
    
    status = Column(SQLEnum(TelegramAccountStatus), default=TelegramAccountStatus.PENDING)
    
    # Who is currently assigned to this account
    assigned_worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    
    # Metrics
    total_messages_sent = Column(Integer, default=0)
    total_work_seconds = Column(Integer, default=0)
    
    last_activity_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_worker = relationship("Worker")

class TelegramRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class TelegramRequest(Base):
    __tablename__ = "telegram_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    account_id = Column(Integer, ForeignKey("telegram_accounts.id"), nullable=True)
    
    request_type = Column(String) # e.g. "CHANGE_PASSWORD", "CHANGE_PHONE", "UPDATE_BIO"
    reason = Column(Text)
    
    status = Column(SQLEnum(TelegramRequestStatus), default=TelegramRequestStatus.PENDING)
    owner_comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    worker = relationship("Worker")
    account = relationship("TelegramAccount")


class TelegramAuditLog(Base):
    __tablename__ = "telegram_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id")) # Which user performed the action
    account_id = Column(Integer, ForeignKey("telegram_accounts.id"), nullable=True) # Which TG account it relates to
    
    action = Column(String) # e.g., "LOGIN", "SEND_MESSAGE", "OPEN_CHAT", "DELETE_MESSAGE", "REVOKE", "TRANSFER"
    details = Column(Text, nullable=True) # JSON or text with extra info
    
    ip_address = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    account = relationship("TelegramAccount")
