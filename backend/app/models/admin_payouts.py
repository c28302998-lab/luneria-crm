from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.models.models import SoftDeleteMixin

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
