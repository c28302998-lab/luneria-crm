from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class EmailAccountBase(BaseModel):
    email_address: EmailStr
    app_password: str
    imap_server: Optional[str] = "imap.gmail.com"
    imap_port: Optional[int] = 993
    smtp_server: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 465
    assigned_worker_id: Optional[int] = None
    assigned_admin_id: Optional[int] = None

class EmailAccountCreate(EmailAccountBase):
    pass

class EmailAccountUpdate(BaseModel):
    app_password: Optional[str] = None
    assigned_worker_id: Optional[int] = None
    assigned_admin_id: Optional[int] = None

class EmailAccountResponse(BaseModel):
    id: int
    email_address: EmailStr
    imap_server: Optional[str]
    imap_port: Optional[int]
    smtp_server: Optional[str]
    smtp_port: Optional[int]
    assigned_worker_id: Optional[int]
    assigned_admin_id: Optional[int]
    status: str
    last_activity_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Message schemas
class EmailMessageList(BaseModel):
    uid: str
    subject: str
    sender: str
    date: datetime
    is_unseen: bool

class EmailMessageDetail(EmailMessageList):
    text: str
    html: str

class EmailSendRequest(BaseModel):
    to_email: EmailStr
    subject: str
    body_text: str
    body_html: Optional[str] = None
