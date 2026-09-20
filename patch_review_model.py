with open('backend/app/models/telegram.py', 'r') as f:
    content = f.read()

review_model = """
class AccountReview(Base):
    __tablename__ = "account_reviews"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("telegram_accounts.id"), index=True)
    previous_worker_id = Column(Integer, ForeignKey("users.id"))
    created_by = Column(String, default="SYSTEM")
    created_at = Column(DateTime, default=datetime.utcnow)
    potential = Column(String, nullable=True) # HIGH, MEDIUM, LOW
    decision = Column(String, nullable=True) # REASSIGN, RE_REGISTER, ARCHIVE
    comment = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True)
"""
if 'class AccountReview' not in content:
    content += '\n' + review_model

with open('backend/app/models/telegram.py', 'w') as f:
    f.write(content)

