import re

with open('backend/app/api/workers.py', 'r') as f:
    content = f.read()

# I need to find the block:
#     # Proactively create a User account for the Worker if it doesn't exist
#     existing_user = db.query(User).filter(User.email == candidate.email).first()
#     if not existing_user and candidate.email:
#         from app.core.security import get_password_hash
#         # Generate a simple default password based on telegram or something, or just a generic one
#         default_password = "password123"
#         new_user = User(
#             email=candidate.email,
#             password_hash=get_password_hash(default_password),
#             name=candidate.first_name,
#             role="WORKER",
#             raw_password=default_password
#         )
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)

replacement = """
    # Proactively create a User account for the Worker if it doesn't exist
    existing_user = db.query(User).filter(User.email == candidate.email).first()
    invite_link = None
    if not existing_user and candidate.email:
        new_user = User(
            email=candidate.email,
            name=candidate.first_name,
            role="WORKER",
            raw_password=None # REMOVED HARDCODED PASSWORD
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        existing_user = new_user
        
    if existing_user:
        # Generate Invite Token
        import uuid
        from datetime import datetime, timedelta
        from app.models.models import InviteToken
        token = str(uuid.uuid4())
        invite = InviteToken(
            token=token,
            user_id=existing_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(invite)
        db.commit()
        # Frontend URL logic: assuming it's available via origin or hardcoded
        invite_link = f"/invite/{token}"
"""

# Replace the block
content = re.sub(
    r"# Proactively create a User account.*?db\.refresh\(new_user\)", 
    replacement.strip(), 
    content, 
    flags=re.DOTALL
)

# Modify response schema to return invite_link
# Wait, WorkerSchema doesn't have invite_link.
# Let's add it dynamically to the response if it's a dict, but FastAPI uses Pydantic.
# Let's just create an exception to return it, or update the schema.
with open('backend/app/api/workers.py', 'w') as f:
    f.write(content)

