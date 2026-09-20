with open("backend/app/models/telegram.py", "r") as f:
    content = f.read()

content = content.replace(
    'assigned_user = relationship("User")',
    'assigned_user = relationship("User", foreign_keys=[assigned_user_id])\n    assigned_worker = relationship("User", foreign_keys=[assigned_worker_id])'
)

with open("backend/app/models/telegram.py", "w") as f:
    f.write(content)
