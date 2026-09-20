import re

with open("backend/app/services/telegram_manager.py", "r") as f:
    content = f.read()

content = content.replace(
    "async def download_message_media(self, account_id: int, chat_id: int, message_id: int) -> bytes:\n        client = self.clients.get(account_id)",
    "async def download_message_media(self, account_id: int, chat_id: int, message_id: int, db=None) -> bytes:\n        client = await self.get_client(account_id, db)"
)

with open("backend/app/services/telegram_manager.py", "w") as f:
    f.write(content)

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

content = content.replace(
    "data = await telegram_manager.download_message_media(account_id, int(chat_id), message_id)",
    "data = await telegram_manager.download_message_media(account_id, int(chat_id), message_id, db)"
)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
