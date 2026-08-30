from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

class User(Base, SoftDeleteMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String) # OWNER, CURATOR, ADMIN, FINANCE
    curator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ACTIVE")

    curator = relationship("User", remote_side=[id], back_populates="admins")
    admins = relationship("User", back_populates="curator")
    candidates = relationship("Candidate", back_populates="admin")
    workers = relationship("Worker", back_populates="admin")

class Candidate(Base, SoftDeleteMixin):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    telegram = Column(String, index=True)
    email = Column(String, index=True)
    country = Column(String)
    age = Column(Integer)
    source = Column(String)
    notes = Column(String)
    status = Column(String, default="NEW")
    files = Column(JSON, default=list)
    files = Column(JSON, default=list)
    admin_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    admin = relationship("User", back_populates="candidates")
    training = relationship("Training", back_populates="candidate", uselist=False)
    worker = relationship("Worker", back_populates="candidate", uselist=False)
    history = relationship("CandidateHistory", back_populates="candidate")

class CandidateHistory(Base):
    __tablename__ = "candidate_history"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    old_status = Column(String, nullable=True)
    new_status = Column(String)
    changed_by = Column(Integer, ForeignKey("users.id"))
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="history")
    user = relationship("User")

class Training(Base, SoftDeleteMixin):
    __tablename__ = "trainings"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    progress = Column(Float, default=0.0)
    tasks = Column(JSON, default=list)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    result = Column(String, nullable=True)

    candidate = relationship("Candidate", back_populates="training")

class Partner(Base, SoftDeleteMixin):
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    contact = Column(String)
    workers_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    workers = relationship("Worker", back_populates="partner")
    payments = relationship("Payment", back_populates="partner")

class Worker(Base, SoftDeleteMixin):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    files = Column(JSON, default=list)
    admin_id = Column(Integer, ForeignKey("users.id"))
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    shift = Column(String, nullable=True)
    account_info = Column(String, nullable=True)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="worker")
    admin = relationship("User", back_populates="workers")
    partner = relationship("Partner", back_populates="workers")
    payments = relationship("Payment", back_populates="worker")

class Payment(Base, SoftDeleteMixin):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    files = Column(JSON, default=list)
    admin_id = Column(Integer, ForeignKey("users.id"))
    partner_id = Column(Integer, ForeignKey("partners.id"))
    amount = Column(Float)
    amount_company = Column(Float, default=0.0)
    amount_worker = Column(Float, default=0.0)
    amount_admin = Column(Float, default=0.0)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="COMPLETED")

    worker = relationship("Worker", back_populates="payments")

    admin = relationship("User")
    partner = relationship("Partner", back_populates="payments")

class Expense(Base, SoftDeleteMixin):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    reason = Column(String)
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    files = Column(JSON, default=list)
    
    creator = relationship("User")

class Task(Base, SoftDeleteMixin):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String, default="MEDIUM")
    deadline = Column(DateTime, nullable=True)
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="NEW")
    files = Column(JSON, default=list)

    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    creator = relationship("User", foreign_keys=[creator_id])

class Report(Base, SoftDeleteMixin):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    files = Column(JSON, default=list)
    admin_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    admin = relationship("User")

class Notification(Base, SoftDeleteMixin):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class Message(Base, SoftDeleteMixin):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    changes = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True) # "CANDIDATE" or "TASK"
    entity_id = Column(Integer, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class Material(Base, SoftDeleteMixin):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    files = Column(JSON, default=list)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User")

class Source(Base, SoftDeleteMixin):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    files = Column(JSON, default=list)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User")

class FileUpload(Base):
    __tablename__ = "file_uploads"
    id = Column(String, primary_key=True, index=True) # UUID
    filename = Column(String)
    content_type = Column(String)
    data = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)

class AccountRequest(Base, SoftDeleteMixin):
    __tablename__ = "account_requests"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    admin_id = Column(Integer, ForeignKey("users.id"))
    admin_telegram = Column(String)
    comment = Column(String)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate")
    admin = relationship("User")

from sqlalchemy import Date
class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    date = Column(Date)
    is_present = Column(Boolean, default=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class UserShift(Base):
    __tablename__ = "user_shifts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.utcnow().date)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    user = relationship("User")
