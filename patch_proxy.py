with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

import re

old_my = """    if user.role != "OWNER":
        query = query.filter(TelegramAccount.assigned_user_id == user.id)"""

new_my = """    if user.role in ["WORKER", "CANDIDATE"]:
        query = query.filter(TelegramAccount.assigned_worker_id == user.id)
    elif user.role == "ADMIN":
        query = query.filter(TelegramAccount.assigned_user_id == user.id)"""

content = content.replace(old_my, new_my)

old_acc = """    if user.role != "OWNER":
        query = query.filter(TelegramAccount.assigned_user_id == user.id)"""

new_acc = """    if user.role in ["WORKER", "CANDIDATE"]:
        query = query.filter(TelegramAccount.assigned_worker_id == user.id)
    elif user.role == "ADMIN":
        query = query.filter(TelegramAccount.assigned_user_id == user.id)"""

content = content.replace(old_acc, new_acc)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
