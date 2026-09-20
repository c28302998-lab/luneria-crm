import re

with open("frontend/src/app/dashboard/layout.tsx", "r") as f:
    content = f.read()

# 1. Remove "Заявки на аккаунт" from ADMIN
# We need to find the block for ADMIN
# Match from "if (role === 'ADMIN') {" to the next "if (role ==="
admin_pattern = r"(if \(role === 'ADMIN'\) \{.*?)(\n\s*if \(role ===)"
def replace_admin(m):
    admin_block = m.group(1)
    # Remove account requests
    admin_block = re.sub(r"\s*\{\s*name:\s*'Заявки на аккаунт'[^\}]+\},", "", admin_block)
    
    # Insert Tasks before Sistema
    tasks_item = "      { group: 'Управление', items: [\n        { name: 'Задачи', href: '/dashboard/tasks', icon: CheckSquare },\n      ]},\n"
    admin_block = admin_block.replace("      { group: 'Система'", tasks_item + "      { group: 'Система'")
    
    return admin_block + m.group(2)

new_content = re.sub(admin_pattern, replace_admin, content, flags=re.DOTALL)

with open("frontend/src/app/dashboard/layout.tsx", "w") as f:
    f.write(new_content)
