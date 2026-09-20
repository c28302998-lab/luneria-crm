from app.db.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

db = SessionLocal()
owner = db.query(User).filter(User.email == "owner@lunery.local").first()
if owner:
    owner.raw_password = "owner123"
    owner.password_hash = get_password_hash("owner123")
    db.commit()
    print("FIXED OWNER")
