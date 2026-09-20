with open("backend/app/api/router.py", "r") as f:
    content = f.read()

content = content.replace("from app.api import balance_requests,\n(", "from app.api import balance_requests, (\n")

with open("backend/app/api/router.py", "w") as f:
    f.write(content)
