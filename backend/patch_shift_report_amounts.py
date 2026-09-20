with open("app/models/models.py", "r") as f:
    content = f.read()

old_notes = 'notes = Column(String, nullable=True)'
new_notes = 'notes = Column(String, nullable=True)\n    worker_amount = Column(Float, nullable=True)\n    admin_amount = Column(Float, nullable=True)'

content = content.replace(old_notes, new_notes)

with open("app/models/models.py", "w") as f:
    f.write(content)

with open("app/schemas/schemas.py", "r") as f:
    content = f.read()

old_schema = 'status: str'
new_schema = 'status: str\n    worker_amount: Optional[float] = None\n    admin_amount: Optional[float] = None'

content = content.replace(old_schema, new_schema)

with open("app/schemas/schemas.py", "w") as f:
    f.write(content)
