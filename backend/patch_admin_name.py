with open("app/models/models.py", "r") as f:
    content = f.read()

old_prop = """    @property
    def worker_name(self):
        return self.worker.name if self.worker else f"Worker #{self.worker_id}"
"""

new_prop = """    @property
    def worker_name(self):
        return self.worker.name if self.worker else f"Worker #{self.worker_id}"

    @property
    def admin_name(self):
        from app.models.models import Candidate, Worker, User
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if not session or not self.worker or not self.worker.email:
            return None
        candidate = session.query(Candidate).filter(Candidate.email == self.worker.email).first()
        if candidate:
            worker_record = session.query(Worker).filter(Worker.candidate_id == candidate.id).first()
            if worker_record and worker_record.admin_id:
                admin_user = session.query(User).filter(User.id == worker_record.admin_id).first()
                return admin_user.name if admin_user else None
        return None
"""

content = content.replace(old_prop, new_prop)
with open("app/models/models.py", "w") as f:
    f.write(content)

with open("app/schemas/schemas.py", "r") as f:
    content = f.read()

old_schema = 'admin_amount: Optional[float] = None'
new_schema = 'admin_amount: Optional[float] = None\n    admin_name: Optional[str] = None'

content = content.replace(old_schema, new_schema)
with open("app/schemas/schemas.py", "w") as f:
    f.write(content)
