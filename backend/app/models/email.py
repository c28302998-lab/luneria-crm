from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base
from .models import SoftDeleteMixin

class EmailAccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    DISABLED = "DISABLED"

class EmailAccount(Base, SoftDeleteMixin):
    __tablename__ = "email_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String, index=True, nullable=False)
    app_password = Column(String, nullable=False)
    
    # Provider settings (default to Gmail)
    imap_server = Column(String, default="imap.gmail.com")
    imap_port = Column(Integer, default=993)
    smtp_server = Column(String, default="smtp.gmail.com")
    smtp_port = Column(Integer, default=465)
    
    status = Column(SQLEnum(EmailAccountStatus), default=EmailAccountStatus.ACTIVE)
    
    # Who is currently assigned to this account
    assigned_worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True) # To know which admin manages it
    
    last_activity_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_worker = relationship("User", foreign_keys=[assigned_worker_id])
    assigned_admin = relationship("User", foreign_keys=[assigned_admin_id])

class EmailRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class EmailRequest(Base):
    __tablename__ = "email_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=True)
    
    request_type = Column(String) # e.g. "NEW_ACCOUNT", "CHANGE_PASSWORD"
    reason = Column(Text)
    
    status = Column(SQLEnum(EmailRequestStatus), default=EmailRequestStatus.PENDING)
    owner_comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")
    account = relationship("EmailAccount")

class EmailAuditLog(Base):
    __tablename__ = "email_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=True)
    
    action = Column(String) # "LOGIN", "SEND_EMAIL", "READ_EMAIL"
    details = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    account = relationship("EmailAccount")


class EmailAccountAssignment(Base):
    __tablename__ = "email_account_assignments"
    id = Column(Integer, primary_key=True, index=True)
    email_account_id = Column(Integer, ForeignKey("email_accounts.id"), index=True)
    worker_id = Column(Integer, ForeignKey("users.id"), index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    reason = Column(String, nullable=True)
    notes = Column(String, nullable=True)
