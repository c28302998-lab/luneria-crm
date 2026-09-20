import re

with open("backend/app/main.py", "r") as f:
    content = f.read()

content = content.replace("ADD COLUMN IF NOT EXISTS", "ADD COLUMN")

with open("backend/app/main.py", "w") as f:
    f.write(content)
