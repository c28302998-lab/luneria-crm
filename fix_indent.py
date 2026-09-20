import re

with open("backend/app/services/telegram_manager.py", "r") as f:
    content = f.read()

# Remove the appended methods from the end
end_methods = """
    async def resolve_entity(self, account_id: int, query: str) -> dict:"""

parts = content.split("    async def resolve_entity(self, account_id: int, query: str) -> dict:")
methods_code = "    async def resolve_entity(self, account_id: int, query: str) -> dict:" + parts[1]

# Insert them before # Global singleton
clean_content = parts[0]
clean_content = clean_content.replace("# Global singleton", methods_code + "\n\n# Global singleton")

with open("backend/app/services/telegram_manager.py", "w") as f:
    f.write(clean_content)
