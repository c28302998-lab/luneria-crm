from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from .user import User

# Candidates
class CandidateBase(BaseModel):
    first_name: str
    telegram: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    age: Optional[int] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    files: List[str] = []

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(CandidateBase):
    first_name: Optional[str] = None
    status: Optional[str] = None

class Candidate(CandidateBase):
    id: int
    status: str
    admin_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# CandidateHistory
class CandidateHistoryBase(BaseModel):
    new_status: str
    old_status: Optional[str] = None
    comment: Optional[str] = None

class UserBasic(BaseModel):
    name: str
    role: str
    class Config:
        from_attributes = True

class CandidateHistory(CandidateHistoryBase):
    id: int
    candidate_id: int
    changed_by: Optional[int] = None
    created_at: datetime
    user: Optional[UserBasic] = None
    class Config:
        from_attributes = True

class CandidateWithHistory(Candidate):
    history: List[CandidateHistory] = []

# Training
class TrainingBase(BaseModel):
    progress: float
    tasks: List[Any] = []
    start_date: datetime
    end_date: Optional[datetime] = None
    result: Optional[str] = None

class TrainingUpdate(BaseModel):
    progress: Optional[float] = None
    tasks: Optional[List[Any]] = None
    end_date: Optional[datetime] = None
    result: Optional[str] = None

class Training(TrainingBase):
    id: int
    candidate_id: int
    class Config:
        from_attributes = True

# Partner
class PartnerBase(BaseModel):
    company_name: str
    contact: Optional[str] = None

class PartnerCreate(PartnerBase):
    pass

class Partner(PartnerBase):
    id: int
    workers_count: int
    created_at: datetime
    class Config:
        from_attributes = True

# Worker
class WorkerBase(BaseModel):
    status: str = "ACTIVE"

class WorkerCreate(WorkerBase):
    candidate_id: int
    partner_id: Optional[int] = None

class WorkerUpdate(BaseModel):
    status: Optional[str] = None
    partner_id: Optional[int] = None

class Worker(WorkerBase):
    id: int
    candidate_id: int
    admin_id: int
    partner_id: Optional[int] = None
    created_at: datetime
    class Config:
        from_attributes = True

# Payment
class PaymentBase(BaseModel):
    amount: float
    amount_company: float = 0.0
    amount_worker: float = 0.0
    amount_admin: float = 0.0

class PaymentCreate(PaymentBase):
    worker_id: int

class Payment(PaymentBase):
    id: int
    worker_id: int
    admin_id: int
    partner_id: int
    date: datetime
    status: str
    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    reason: str
    amount: float

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    date: datetime
    created_by: int
    class Config:
        from_attributes = True

# Task
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    deadline: Optional[datetime] = None
    status: str = "NEW"

class TaskCreate(TaskBase):
    assigned_user_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    assigned_user_id: Optional[int] = None

class Task(TaskBase):
    id: int
    assigned_user_id: int
    creator_id: int
    class Config:
        from_attributes = True

# Report
class ReportBase(BaseModel):
    type: str
    data: dict

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int
    admin_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Notification
class NotificationBase(BaseModel):
    type: str
    message: str

class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Message
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: int

class Message(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

# AuditLog
class AuditLog(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    changes: dict
    created_at: datetime
    class Config:
        from_attributes = True
