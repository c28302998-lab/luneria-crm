from app.db.database import SessionLocal
from app.models.models import User

db = SessionLocal()
u = db.query(User).filter(User.email == 'worker8@lunery.local').first()
if u:
    print(f"User: {u.id} {u.name} {u.email} deleted:{u.is_deleted} role:{u.role}")
else:
    print("User not found!")
db.close()
