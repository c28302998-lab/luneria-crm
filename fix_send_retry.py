import re

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

old_send = """        try:
            peer_id = int(req.chat_id)
        except:
            peer_id = req.chat_id
            
        sent = await client.send_message(peer_id, req.text)"""

new_send = """        try:
            peer_id = int(req.chat_id)
        except:
            peer_id = req.chat_id
            
        try:
            sent = await client.send_message(peer_id, req.text)
        except ValueError as e:
            if "entity" in str(e).lower() or "find" in str(e).lower():
                # Cache missing on this worker. Fetch dialogs to populate cache.
                await client.get_dialogs(limit=200)
                sent = await client.send_message(peer_id, req.text)
            else:
                raise e"""

content = content.replace(old_send, new_send)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
