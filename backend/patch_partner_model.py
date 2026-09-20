with open("backend/app/models/models.py", "r") as f:
    content = f.read()

import re

old_partner = """class Partner(Base, SoftDeleteMixin):
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    contact = Column(String)
    workers_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    workers = relationship("Worker", back_populates="partner")
    payments = relationship("Payment", back_populates="partner")"""

new_partner = """class Partner(Base, SoftDeleteMixin):
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
    workers_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    workers = relationship("Worker", back_populates="partner")
    payments = relationship("Payment", back_populates="partner")"""

content = content.replace(old_partner, new_partner)

with open("backend/app/models/models.py", "w") as f:
    f.write(content)
