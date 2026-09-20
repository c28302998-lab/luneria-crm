import re

with open("backend/app/services/telegram_manager.py", "r") as f:
    content = f.read()

# Fix download_message_media
content = content.replace(
    "async def download_message_media(self, account_id: int, chat_id: int, message_id: int, db=None) -> bytes:\n        client = await self.get_client(account_id, db)",
    "async def download_message_media(self, account_id: int, chat_id: int, message_id: int, session_string: str = None) -> bytes:\n        client = await self.get_client(account_id, session_string) if session_string else self.clients.get(account_id)\n        if not client:\n            raise Exception('Client not connected')"
)

# Fix resolve_entity
content = content.replace(
    "async def resolve_entity(self, account_id: int, query: str, db=None) -> dict:\n        client = await self.get_client(account_id, db)",
    "async def resolve_entity(self, account_id: int, query: str, session_string: str = None) -> dict:\n        client = await self.get_client(account_id, session_string) if session_string else self.clients.get(account_id)\n        if not client:\n            raise Exception('Client not connected')"
)

# Fix get_profile_photo
content = content.replace(
    "async def get_profile_photo(self, account_id: int, entity_id: int, db=None) -> bytes:\n        client = await self.get_client(account_id, db)",
    "async def get_profile_photo(self, account_id: int, entity_id: int, session_string: str = None) -> bytes:\n        client = await self.get_client(account_id, session_string) if session_string else self.clients.get(account_id)\n        if not client:\n            raise Exception('Client not connected')"
)

with open("backend/app/services/telegram_manager.py", "w") as f:
    f.write(content)
