with open('backend/app/models/telegram.py', 'r') as f:
    content = f.read()

if "responsible_admin_id =" not in content:
    content = content.replace('assigned_worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)', 'assigned_worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)\n    responsible_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)')

with open('backend/app/models/telegram.py', 'w') as f:
    f.write(content)

with open('backend/app/models/email.py', 'r') as f:
    content = f.read()

if "responsible_admin_id =" not in content:
    content = content.replace('assigned_admin_id = Column(Integer, ForeignKey("users.id"))', 'assigned_admin_id = Column(Integer, ForeignKey("users.id"))\n    responsible_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)')

with open('backend/app/models/email.py', 'w') as f:
    f.write(content)

