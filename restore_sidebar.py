import re

with open("frontend/src/app/dashboard/layout.tsx", "r") as f:
    content = f.read()

# For OWNER
content = content.replace(
    "{ group: 'Доступы', items: [\n        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },",
    "{ group: 'Доступы', items: [\n        { name: 'Заявки на аккаунт', href: '/dashboard/account-requests', icon: Key },\n        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },"
)

# For ADMIN
content = content.replace(
    "{ group: 'Доступы', items: [\n        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },",
    "{ group: 'Доступы', items: [\n        { name: 'Мои Заявки', href: '/dashboard/account-requests', icon: Key },\n        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },"
)

with open("frontend/src/app/dashboard/layout.tsx", "w") as f:
    f.write(content)
