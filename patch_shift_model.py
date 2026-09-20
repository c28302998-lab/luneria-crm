import re

with open('backend/app/models/models.py', 'r') as f:
    content = f.read()

shift_model = """
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
"""

if "class Shift(Base):" not in content:
    content += "\n" + shift_model

with open('backend/app/models/models.py', 'w') as f:
    f.write(content)

