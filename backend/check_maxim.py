from app.db.database import SessionLocal
from app.models.models import User

db = SessionLocal()
users = db.query(User).filter(User.name.ilike('%Максим%')).all()
for u in users:
    print(f"User: {u.id} {u.name} {u.email} deleted:{u.is_deleted}")
db.close()
