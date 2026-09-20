import sys
sys.path.append(".")
from app.db.session import SessionLocal
from app.models.models import Worker, User, Candidate

db = SessionLocal()
deleted_workers = db.query(Worker).filter(Worker.is_deleted == True).all()

count = 0
for w in deleted_workers:
    if w.candidate and w.candidate.email:
        u = db.query(User).filter(User.email == w.candidate.email).first()
        if u and not u.is_deleted:
            u.is_deleted = True
            count += 1

db.commit()
print(f"Fixed {count} users")
db.close()
