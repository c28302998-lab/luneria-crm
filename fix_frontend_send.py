import re

with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

# Replace send message target
old_send = "await api.post(`/telegram/proxy/send${selectedAccountId ? '?account_id='+selectedAccountId : ''}`, { chat_id: activeChat.id, text });"
new_send = "const targetId = activeChat.username ? activeChat.username : (activeChat.phone ? activeChat.phone : activeChat.id);\n      await api.post(`/telegram/proxy/send${selectedAccountId ? '?account_id='+selectedAccountId : ''}`, { chat_id: targetId, text });"
content = content.replace(old_send, new_send)

with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
