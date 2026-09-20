from app.db.database import SessionLocal
from app.models.models import User, Worker, Candidate
db = SessionLocal()
print("USERS matching German:")
users = db.query(User).filter(User.name.ilike('%Герман%')).all()
for u in users:
    print(u.id, u.name, u.role)
print("WORKERS matching German:")
workers = db.query(Worker).all()
for w in workers:
    if w.user and w.user.name and 'Герман' in w.user.name:
        print("Worker ID:", w.id, "User ID:", w.user.id, w.user.name, w.user.role)
    elif w.candidate:
        if 'Герман' in w.candidate.first_name:
            print("Worker ID:", w.id, "Candidate ID:", w.candidate.id, w.candidate.first_name)
