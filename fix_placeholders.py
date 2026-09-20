import re

# 1. Update attendance/page.tsx
with open("frontend/src/app/dashboard/attendance/page.tsx", "r") as f:
    content = f.read()

content = content.replace('placeholder="10:00 - 18:00"', 'placeholder="Напр. 10:00 - 18:00"')
content = content.replace('placeholder="Название аккаунта"', 'placeholder="Впишите аккаунт..."')

with open("frontend/src/app/dashboard/attendance/page.tsx", "w") as f:
    f.write(content)

# 2. Update workers/[id]/page.tsx
with open("frontend/src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

content = content.replace('placeholder="10:00 - 18:00"', 'placeholder="Напр. 10:00 - 18:00"')
content = content.replace('placeholder="Название аккаунта"', 'placeholder="Впишите аккаунт..."')

with open("frontend/src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
