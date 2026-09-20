with open('backend/app/models/models.py', 'r') as f:
    content = f.read()

new_model = """
class InviteToken(Base):
    __tablename__ = "invite_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
"""

if 'class InviteToken' not in content:
    content = content.replace('class User(Base, SoftDeleteMixin):', new_model + '\nclass User(Base, SoftDeleteMixin):')

with open('backend/app/models/models.py', 'w') as f:
    f.write(content)
