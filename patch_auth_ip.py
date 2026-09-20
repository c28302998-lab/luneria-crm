with open("backend/app/api/auth.py", "r") as f:
    content = f.read()

import re

old_ip = "ip = form_data.username # We use username as key since we don't have request.client.host easily here without Request object."
new_ip = "ip = form_data.username.strip() # We use username as key since we don't have request.client.host easily here without Request object."

content = content.replace(old_ip, new_ip)

with open("backend/app/api/auth.py", "w") as f:
    f.write(content)
