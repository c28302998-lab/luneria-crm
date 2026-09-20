import re

with open("backend/app/schemas/schemas.py", "r") as f:
    content = f.read()

content = content.replace("    notes: Optional[str] = None\n\nclass SourceCreate(SourceBase):", "\nclass SourceCreate(SourceBase):")

with open("backend/app/schemas/schemas.py", "w") as f:
    f.write(content)
