with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

import re

old_loop = """        chats = []
        for d in dialogs:
            chat_id_str = str(d.id)
            chat_name = d.name
            
            is_masked = False
            custom_name = aliases.get(chat_id_str)"""

new_loop = """        chats = []
        me = await client.get_me()
        for d in dialogs:
            chat_id_str = str(d.id)
            chat_name = d.name
            
            if d.entity and d.entity.id == me.id:
                chat_name = "Избранное"
            
            is_masked = False
            custom_name = aliases.get(chat_id_str)"""

content = content.replace(old_loop, new_loop)

old_append = """            chats.append({
                "id": chat_id_str,
                "name": chat_name,
                "is_user": d.is_user,
                "is_group": d.is_group,
                "is_channel": d.is_channel,
                "unread_count": d.unread_count,
                "message": d.message.text if d.message else "",
                "date": d.date.isoformat() if d.date else None,
                "is_masked": is_masked,
                "original_name": d.name if user.role == "OWNER" else None
            })"""

new_append = """            chats.append({
                "id": chat_id_str,
                "name": chat_name,
                "is_user": d.is_user,
                "is_group": d.is_group,
                "is_channel": d.is_channel,
                "unread_count": d.unread_count,
                "message": d.message.text if d.message else "",
                "date": d.date.isoformat() if d.date else None,
                "is_masked": is_masked,
                "original_name": d.name if user.role == "OWNER" else None,
                "archived": getattr(d, 'archived', False)
            })"""

content = content.replace(old_append, new_append)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
