with open('backend/app/models/telegram.py', 'r') as f:
    content = f.read()

assignment_model = """
class AccountAssignment(Base):
    __tablename__ = "account_assignments"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("telegram_accounts.id"), index=True)
    worker_id = Column(Integer, ForeignKey("users.id"), index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    reason = Column(String, nullable=True)
    notes = Column(String, nullable=True)
"""
if 'class AccountAssignment' not in content:
    content += '\n' + assignment_model

with open('backend/app/models/telegram.py', 'w') as f:
    f.write(content)

with open('backend/app/models/email.py', 'r') as f:
    content = f.read()

email_assignment_model = """
class EmailAccountAssignment(Base):
    __tablename__ = "email_account_assignments"
    id = Column(Integer, primary_key=True, index=True)
    email_account_id = Column(Integer, ForeignKey("email_accounts.id"), index=True)
    worker_id = Column(Integer, ForeignKey("users.id"), index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    reason = Column(String, nullable=True)
    notes = Column(String, nullable=True)
"""
if 'class EmailAccountAssignment' not in content:
    content += '\n' + email_assignment_model

with open('backend/app/models/email.py', 'w') as f:
    f.write(content)

