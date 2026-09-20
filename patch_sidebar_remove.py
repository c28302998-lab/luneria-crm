import re

with open("frontend/src/app/dashboard/layout.tsx", "r") as f:
    content = f.read()

# For OWNER
content = content.replace("{ name: 'Заявки на аккаунт', href: '/dashboard/account-requests', icon: Key },\n", "")
content = content.replace("        { name: 'Аккаунты (OnlyFans)', href: '/dashboard/accounts', icon: Key },\n", "")

# For ADMIN
content = content.replace("        { name: 'Мои Заявки', href: '/dashboard/account-requests', icon: Key },\n", "")
content = content.replace("        { name: 'Мои Аккаунты', href: '/dashboard/accounts', icon: Key },\n", "")

with open("frontend/src/app/dashboard/layout.tsx", "w") as f:
    f.write(content)
