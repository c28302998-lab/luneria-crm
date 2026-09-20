with open("frontend/src/app/dashboard/layout.tsx", "r") as f:
    content = f.read()

# Fix for OWNER
content = content.replace(
    "{ name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },\n        { name: 'Аккаунты Работников', href: '/dashboard/crm-accounts', icon: Users },",
    "{ name: 'Заявки на аккаунт', href: '/dashboard/account-requests', icon: Key },\n        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },\n        { name: 'Аккаунты Работников', href: '/dashboard/crm-accounts', icon: Users },"
)

with open("frontend/src/app/dashboard/layout.tsx", "w") as f:
    f.write(content)
