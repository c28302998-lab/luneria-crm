import re

with open("backend/app/services/telegram_manager.py", "r") as f:
    content = f.read()

content = content.replace(
    "async def get_profile_photo(self, account_id: int, entity_id: int) -> bytes:\n        client = self.clients.get(account_id)",
    "async def get_profile_photo(self, account_id: int, entity_id: int, db=None) -> bytes:\n        client = await self.get_client(account_id, db)"
)

with open("backend/app/services/telegram_manager.py", "w") as f:
    f.write(content)

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

content = content.replace(
    "async def get_avatar(account_id: int, entity_id: int):",
    "async def get_avatar(account_id: int, entity_id: int, db: Session = Depends(get_db)):"
)
content = content.replace(
    "data = await telegram_manager.get_profile_photo(account_id, entity_id)",
    "data = await telegram_manager.get_profile_photo(account_id, entity_id, db)"
)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
