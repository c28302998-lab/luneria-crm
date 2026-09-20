import re

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

content = content.replace(
    "chat = await telegram_manager.resolve_entity(acc.id, query, db)",
    "chat = await telegram_manager.resolve_entity(acc.id, query, acc.session_string)"
)

content = content.replace(
    "data = await telegram_manager.download_message_media(account_id, int(chat_id), message_id, db)",
    "data = await telegram_manager.download_message_media(account_id, int(chat_id), message_id, acc.session_string)"
)
# Wait, get_message_media original code in telegram_proxy was NOT using db because I replaced it earlier?
# Ah, I replaced:
# "data = await telegram_manager.download_message_media(account_id, int(chat_id), message_id)"
# with:
# "data = await telegram_manager.download_message_media(account_id, int(chat_id), message_id, db)"
# But wait, looking at my grep, it's actually:
# "data = await telegram_manager.download_message_media(acc.id, peer_id, message_id)"!
# I didn't replace it in fix_media_db.py because the regex didn't match!
