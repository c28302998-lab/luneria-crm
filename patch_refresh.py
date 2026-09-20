with open("backend/app/api/telegram_admin.py", "r") as f:
    content = f.read()

import re

# Add db.refresh(acc) right after db.commit() in assign_account
content = content.replace("        db.commit()\n        \n        # Audit log", "        db.commit()\n        db.refresh(acc)\n        \n        # Audit log")

with open("backend/app/api/telegram_admin.py", "w") as f:
    f.write(content)
