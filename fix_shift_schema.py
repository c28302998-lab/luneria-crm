import re

with open("backend/app/schemas/schemas.py", "r") as f:
    content = f.read()

content = content.replace(
    "files: List[str]\n    status: str",
    "files: List[str]\n    notes: Optional[str] = None\n    status: str"
)

with open("backend/app/schemas/schemas.py", "w") as f:
    f.write(content)
