with open('backend/app/api/telegram_admin.py', 'r') as f:
    content = f.read()

content = "from app.core.dependencies import RoleChecker\n" + content

with open('backend/app/api/telegram_admin.py', 'w') as f:
    f.write(content)
