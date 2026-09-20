from app.db.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

db = SessionLocal()
owner = db.query(User).filter(User.email == "owner@lunery.local").first()
if owner:
    owner.raw_password = "password123"
    owner.password_hash = get_password_hash("password123")
    db.commit()
    print("FIXED OWNER TO password123")
