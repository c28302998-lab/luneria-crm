from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Boolean, LargeBinary, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)


class InviteToken(Base):
    __tablename__ = "invite_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")

class User(Base, SoftDeleteMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    raw_password = Column(String, nullable=True)
    role = Column(String) # OWNER, CURATOR, ADMIN, FINANCE
    curator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ACTIVE")
    balance = Column(Float, default=0.0)
    payout_date = Column(Date, nullable=True)

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
    experience = Column(String, nullable=True)
    english_level = Column(String, nullable=True)
    desired_income = Column(String, nullable=True)
    is_studying = Column(Boolean, nullable=True)
    is_longterm = Column(Boolean, nullable=True)
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
    referrer_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
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
    referrer_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
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
    country = Column(String, nullable=True)
    seats = Column(Integer, default=0)
    payment_terms = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    registration_time = Column(String, nullable=True)
    response_time = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    last_contact_date = Column(String, nullable=True)
    advances = Column(String, nullable=True)
    schedules = Column(String, nullable=True)
    workers_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    workers = relationship("Worker", back_populates="partner")
    payments = relationship("Payment", back_populates="partner")

class Worker(Base, SoftDeleteMixin):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    referrer_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
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
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    
    candidate_name = Column(String)
    age = Column(String)
    account_type = Column(String)
    admin_nickname = Column(String)
    candidate_nickname = Column(String, nullable=True)
    candidate_tg = Column(String)
    questionnaire = Column(String)
    
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    status = Column(String, default="PENDING")
    issued_account_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate")
    admin = relationship("User")
    partner = relationship("Partner")
    admin = relationship("User")

from sqlalchemy import Date
class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    date = Column(Date)
    is_present = Column(Boolean, default=False)
    status = Column(String, default="APPROVED")
    income = Column(Float, nullable=True)
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

class Account(Base, SoftDeleteMixin):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, index=True)
    account_number = Column(String, nullable=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    issued_at = Column(DateTime, nullable=True)
    status = Column(String, default="FREE") # FREE, ISSUED, IN_PROGRESS, ISSUE, NEEDS_REPLACEMENT, RETURNED
    created_at = Column(DateTime, default=datetime.utcnow)

    worker = relationship("Worker")
    partner = relationship("Partner")

class AccountEmail(Base, SoftDeleteMixin):
    __tablename__ = "account_emails"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    linked_account_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account")

class ShiftReport(Base, SoftDeleteMixin):
    __tablename__ = "shift_reports"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("users.id")) # Wait! Workers authenticate as Users. But they are also in the workers table.
    amount = Column(Float)
    files = Column(JSON, default=list) # Array of URLs/paths to screenshots
    notes = Column(String, nullable=True)
    worker_amount = Column(Float, nullable=True)
    admin_amount = Column(Float, nullable=True)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    worker = relationship("User", foreign_keys=[worker_id])

    @property
    def worker_name(self):
        return self.worker.name if self.worker else f"Worker #{self.worker_id}"

    @property
    def admin_name(self):
        from app.models.models import Candidate, Worker, User
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if not session or not self.worker or not self.worker.email:
            return None
        candidate = session.query(Candidate).filter(Candidate.email == self.worker.email).first()
        if candidate:
            worker_record = session.query(Worker).filter(Worker.candidate_id == candidate.id).first()
            if worker_record and worker_record.admin_id:
                admin_user = session.query(User).filter(User.id == worker_record.admin_id).first()
                return admin_user.name if admin_user else None
        return None

class AdminPayout(Base, SoftDeleteMixin):
    __tablename__ = "admin_payouts"
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    date = Column(Date)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    admin = relationship("User", foreign_keys=[admin_id])
    creator = relationship("User", foreign_keys=[created_by])

class BalanceRequest(Base):
    __tablename__ = "balance_requests"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String) # FINE, BONUS
    amount = Column(Float)
    reason = Column(String)
    proof_url = Column(String, nullable=True)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)

    worker = relationship("User", foreign_keys=[worker_id])

    @property
    def worker_name(self):
        return self.worker.name if self.worker else f"Worker #{self.worker_id}"

    @property
    def admin_name(self):
        from app.models.models import Candidate, Worker, User
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if not session or not self.worker or not self.worker.email:
            return None
        candidate = session.query(Candidate).filter(Candidate.email == self.worker.email).first()
        if candidate:
            worker_record = session.query(Worker).filter(Worker.candidate_id == candidate.id).first()
            if worker_record and worker_record.admin_id:
                admin_user = session.query(User).filter(User.id == worker_record.admin_id).first()
                return admin_user.name if admin_user else None
        return None
    admin = relationship("User", foreign_keys=[admin_id])


class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("users.id"), index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), index=True)
    shift_type = Column(String, default="DAY") # DAY, NIGHT
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="ACTIVE") # ACTIVE, PENDING_REVIEW, APPROVED, REJECTED
    report_data = Column(JSON, nullable=True) 
    stats = Column(JSON, nullable=True) 
