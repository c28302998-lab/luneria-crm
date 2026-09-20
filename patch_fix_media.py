with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

import re

old_def = "async def get_message_media(account_id: int, chat_id: str, message_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):"
new_def = "async def get_message_media(account_id: int, chat_id: str, message_id: int, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):"
content = content.replace(old_def, new_def)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
