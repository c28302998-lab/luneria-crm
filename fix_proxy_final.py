import re

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

content = content.replace("from .auth import get_current_user, RoleChecker", "from .auth import get_current_user")

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
