with open("backend/app/api/router.py", "r") as f:
    content = f.read()

content = content.replace("from app.api import balance_requests, (\n    users,", "from app.api import (\n    balance_requests, users,")

with open("backend/app/api/router.py", "w") as f:
    f.write(content)
