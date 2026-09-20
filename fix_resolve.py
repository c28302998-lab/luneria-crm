import re

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

old_def = 'async def resolve_entity(query: str, account_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN", "WORKER", "CURATOR"]))):'
new_def = 'async def resolve_entity(query: str, db: Session = Depends(get_db), acc: TelegramAccount = Depends(get_user_account), user: User = Depends(get_current_user)):'

content = content.replace(old_def, new_def)
content = content.replace('chat = await telegram_manager.resolve_entity(account_id, query)', 'chat = await telegram_manager.resolve_entity(acc.id, query)')

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
