with open("backend/app/api/telegram_admin.py", "r") as f:
    content = f.read()

import re

# Add imports if not present
if "from app.services.google_sheets" not in content:
    content = content.replace(
        "from fastapi import APIRouter, Depends, HTTPException",
        "from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks\nfrom app.services.google_sheets import sync_account_to_sheets\nimport datetime"
    )

with open("backend/app/api/telegram_admin.py", "w") as f:
    f.write(content)
