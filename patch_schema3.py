import re

with open("backend/app/schemas/schemas.py", "r") as f:
    content = f.read()

content = content.replace("    files: List[str] = []\n    notes: Optional[str] = None\n\nclass CandidateCreate", "    files: List[str] = []\n\nclass CandidateCreate")

with open("backend/app/schemas/schemas.py", "w") as f:
    f.write(content)
