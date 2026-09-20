import re
with open('backend/app/api/workers.py', 'r') as f:
    content = f.read()

# I need to set worker.invite_link = invite_link before returning
content = content.replace("return worker", "worker.invite_link = invite_link\n    return worker")

with open('backend/app/api/workers.py', 'w') as f:
    f.write(content)
