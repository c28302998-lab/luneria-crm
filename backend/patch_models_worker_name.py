with open("app/models/models.py", "r") as f:
    content = f.read()

old_rel = 'worker = relationship("User", foreign_keys=[worker_id])'
new_rel = '''worker = relationship("User", foreign_keys=[worker_id])

    @property
    def worker_name(self):
        return self.worker.name if self.worker else f"Worker #{self.worker_id}"'''

content = content.replace(old_rel, new_rel)

with open("app/models/models.py", "w") as f:
    f.write(content)

with open("app/schemas/schemas.py", "r") as f:
    content = f.read()

old_schema = 'worker_id: int'
new_schema = 'worker_id: int\n    worker_name: str | None = None'

content = content.replace(old_schema, new_schema)

with open("app/schemas/schemas.py", "w") as f:
    f.write(content)
