import re

with open("backend/app/models/telegram.py", "r") as f:
    content = f.read()

old_assigned = 'assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)'
new_assigned = 'assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)\n    assigned_worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)\n    worker_note = Column(Text, nullable=True)'

content = content.replace(old_assigned, new_assigned)

with open("backend/app/models/telegram.py", "w") as f:
    f.write(content)
