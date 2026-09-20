from app.db.database import SessionLocal
from app.models.models import User, Worker, Candidate
from app.core.security import get_password_hash
import string
import random

db = SessionLocal()
worker = db.query(Worker).filter(Worker.id == 3).first()
if worker:
    candidate = db.query(Candidate).filter(Candidate.id == worker.candidate_id).first()
    if candidate:
        if not candidate.email:
            candidate.email = f"worker{worker.id}@lunery.local"
        
        new_password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
        
        try:
            new_user = User(
                email=candidate.email,
                password_hash=get_password_hash(new_password),
                name=candidate.first_name or f"Worker {worker.id}",
                role="WORKER"
            )
            db.add(new_user)
            db.commit()
            print("SUCCESS")
        except Exception as e:
            print(f"ERROR: {e}")
            db.rollback()
else:
    print("No worker 3")
