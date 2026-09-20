with open('backend/app/api/telegram_admin.py', 'r') as f:
    content = f.read()

content = content.replace("from app.core.dependencies import get_current_user", "from app.core.dependencies import get_current_user, RoleChecker")

with open('backend/app/api/telegram_admin.py', 'w') as f:
    f.write(content)
