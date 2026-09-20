import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.db.database import SessionLocal
from app.models.models import Candidate, Worker, User, InviteToken

db = SessionLocal()

# Delete dummy if exists
db.query(Worker).filter(Worker.candidate_id == 9999).delete()
db.query(Candidate).filter(Candidate.id == 9999).delete()
db.query(User).filter(User.email == "dummy_candidate@test.com").delete()
db.commit()

# Create dummy candidate
cand = Candidate(id=9999, first_name="Dummy", telegram="dummy", email="dummy_candidate@test.com", status="APPROVED")
db.add(cand)
db.commit()

# Simulate workers.py logic
# Proactively create a User account for the Worker if it doesn't exist
existing_user = db.query(User).filter(User.email == cand.email).first()
invite_link = None
if not existing_user and cand.email:
    new_user = User(
        email=cand.email,
        name=cand.first_name,
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
    token = str(uuid.uuid4())
    invite = InviteToken(
        token=token,
        user_id=existing_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invite)
    db.commit()
    invite_link = f"/invite/{token}"

print(f"Invite link generated: {invite_link}")
db.close()
