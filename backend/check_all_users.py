from app.db.database import SessionLocal
from app.models.models import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f"User: {u.id} {u.name} (Role: {u.role}, Deleted: {u.is_deleted})")
db.close()
