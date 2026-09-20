with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

import re

old_return = 'return [{"id": a.id, "name": a.name, "phone": a.phone, "setup_checklist": a.setup_checklist, "issue_request_status": a.issue_request_status, "two_fa_password": a.two_fa_password if a.issue_request_status == "APPROVED" else None} for a in accs]'
new_return = 'return [{"id": a.id, "name": a.name, "phone": a.phone, "username": a.username, "setup_checklist": a.setup_checklist, "issue_request_status": a.issue_request_status, "two_fa_password": a.two_fa_password if a.issue_request_status == "APPROVED" else None} for a in accs]'

content = content.replace(old_return, new_return)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
