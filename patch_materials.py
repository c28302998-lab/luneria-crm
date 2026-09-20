import re

with open("backend/app/api/materials.py", "r") as f:
    content = f.read()

content = content.replace(
    "material = Material(**material_in.dict(), created_by=current_user.id)",
    "data = material_in.dict()\n    if 'notes' in data:\n        del data['notes']\n    material = Material(**data, created_by=current_user.id)"
)

with open("backend/app/api/materials.py", "w") as f:
    f.write(content)
