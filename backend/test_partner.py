from app.db.database import SessionLocal
from app.models.models import Worker, Partner, User
db = SessionLocal()
workers = db.query(Worker).all()
for w in workers:
    print(w.id, w.partner_id)
