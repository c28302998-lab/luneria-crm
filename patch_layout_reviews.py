import re

with open('frontend/src/app/dashboard/layout.tsx', 'r') as f:
    content = f.read()

new_link = "        { name: 'Ревью Аккаунтов', href: '/dashboard/reviews', icon: CheckSquare },"
if "href: '/dashboard/reviews'" not in content:
    content = content.replace("        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },", "        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },\n" + new_link)
    
with open('frontend/src/app/dashboard/layout.tsx', 'w') as f:
    f.write(content)
