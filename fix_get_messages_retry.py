import re

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

old_get = """        try:
            peer_id = int(chat_id)
        except:
            peer_id = chat_id
            
        msgs = await client.get_messages(peer_id, limit=50)"""

new_get = """        try:
            peer_id = int(chat_id)
        except:
            peer_id = chat_id
            
        try:
            msgs = await client.get_messages(peer_id, limit=50)
        except ValueError as e:
            if "entity" in str(e).lower() or "find" in str(e).lower():
                await client.get_dialogs(limit=200)
                msgs = await client.get_messages(peer_id, limit=50)
            else:
                raise e"""

content = content.replace(old_get, new_get)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
