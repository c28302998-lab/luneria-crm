with open("app/models/models.py", "r") as f:
    content = f.read()

new_model = """
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
    admin = relationship("User", foreign_keys=[admin_id])
"""

content = content + new_model

with open("app/models/models.py", "w") as f:
    f.write(content)
