from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from .user import User
from .schemas import WorkerResponse

class TelegramAccountBase(BaseModel):
    name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    assigned_worker_id: Optional[int] = None
    status: str

class TelegramAccountCreate(TelegramAccountBase):
    session_string: str

class TelegramAccountUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    assigned_worker_id: Optional[int] = None
    status: Optional[str] = None

class TelegramAccountResponse(TelegramAccountBase):
    id: int
    total_messages_sent: int
    total_work_seconds: int
    last_activity_at: Optional[datetime] = None
    created_at: datetime
    assigned_worker: Optional[WorkerResponse] = None
    
    class Config:
        from_attributes = True

class TelegramRequestBase(BaseModel):
    request_type: str
    reason: str
    account_id: Optional[int] = None

class TelegramRequestCreate(TelegramRequestBase):
    pass

class TelegramRequestResponse(TelegramRequestBase):
    id: int
    worker_id: int
    status: str
    owner_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    worker: Optional[WorkerResponse] = None
    account: Optional[TelegramAccountResponse] = None
    
    class Config:
        from_attributes = True

class TelegramAuditLogResponse(BaseModel):
    id: int
    user_id: int
    account_id: Optional[int] = None
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    created_at: datetime
    user: Optional[User] = None
    account: Optional[TelegramAccountResponse] = None
    
    class Config:
        from_attributes = True
