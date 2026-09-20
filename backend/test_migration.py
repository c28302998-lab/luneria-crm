from app.db.database import SessionLocal
from app.models.models import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    if not u.raw_password:
        if "worker" in u.email:
            u.raw_password = "password123"
        elif "owner" in u.email:
            u.raw_password = "password"
db.commit()
print("MIGRATED")
