import re

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

# Fix resolve_entity
content = content.replace("await telegram_manager.resolve_entity(acc.id, query, db)", "await telegram_manager.resolve_entity(acc.id, query, acc.session_string)")

# Fix get_message_media
content = content.replace("await telegram_manager.download_message_media(acc.id, peer_id, message_id)", "await telegram_manager.download_message_media(acc.id, peer_id, message_id, acc.session_string)")

# Fix get_avatar
old_avatar = """async def get_avatar(account_id: int, entity_id: int, db: Session = Depends(get_db)):
    try:
        cache_dir = "uploads/avatars"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{account_id}_{entity_id}.jpg")
        
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                data = f.read()
            if not data:
                return {"error": "No avatar"}
        else:
            data = await telegram_manager.get_profile_photo(account_id, entity_id, db)"""

new_avatar = """async def get_avatar(account_id: int, entity_id: int, db: Session = Depends(get_db)):
    try:
        cache_dir = "uploads/avatars"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{account_id}_{entity_id}.jpg")
        
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                data = f.read()
            if not data:
                return {"error": "No avatar"}
        else:
            acc = db.query(TelegramAccount).get(account_id)
            if not acc: return {"error": "No avatar"}
            data = await telegram_manager.get_profile_photo(account_id, entity_id, acc.session_string)"""

content = content.replace(old_avatar, new_avatar)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
