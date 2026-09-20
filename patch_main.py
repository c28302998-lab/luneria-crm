with open('backend/app/main.py', 'r') as f:
    content = f.read()

if 'from app.api import emails' not in content:
    content = content.replace(
        'from app.api import telegram, telegram_admin',
        'from app.api import telegram, telegram_admin, emails'
    )
    content = content.replace(
        'app.include_router(telegram_admin.router, prefix="/api/v1/telegram/admin", tags=["telegram_admin"])',
        'app.include_router(telegram_admin.router, prefix="/api/v1/telegram/admin", tags=["telegram_admin"])\napp.include_router(emails.router, prefix="/api/v1/emails", tags=["emails"])'
    )
    with open('backend/app/main.py', 'w') as f:
        f.write(content)
    print("Patched main.py")
else:
    print("Already patched")
