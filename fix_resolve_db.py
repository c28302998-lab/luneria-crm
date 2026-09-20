import re

with open("backend/app/services/telegram_manager.py", "r") as f:
    content = f.read()

content = content.replace(
    "async def resolve_entity(self, account_id: int, query: str) -> dict:\n        client = self.clients.get(account_id)",
    "async def resolve_entity(self, account_id: int, query: str, db=None) -> dict:\n        client = await self.get_client(account_id, db)"
)

with open("backend/app/services/telegram_manager.py", "w") as f:
    f.write(content)

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

content = content.replace(
    "chat = await telegram_manager.resolve_entity(acc.id, query)",
    "chat = await telegram_manager.resolve_entity(acc.id, query, db)"
)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
