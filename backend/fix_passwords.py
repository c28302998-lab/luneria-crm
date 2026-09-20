from app.db.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

db = SessionLocal()
users = db.query(User).all()
for u in users:
    if u.raw_password:
        # Force the hash to match the raw_password we are displaying
        u.password_hash = get_password_hash(u.raw_password)
db.commit()
print("FIXED")
