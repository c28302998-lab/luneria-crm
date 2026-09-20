import re

with open('frontend/src/app/dashboard/layout.tsx', 'r') as f:
    content = f.read()

# Replace Worker links
content = content.replace("{ name: 'Сдать смену', href: '/dashboard/shift-report', icon: CheckSquare },", "{ name: 'Мои Смены', href: '/dashboard/my-shifts', icon: Clock },")

# Replace Admin links
content = content.replace("{ name: 'Одобрение смен', href: '/dashboard/attendance', icon: ClipboardCheck },", "")
content = content.replace("{ name: 'Отчеты работников', href: '/dashboard/worker-reports', icon: Clock },", "")
content = content.replace("{ name: 'Логи Работы', href: '/dashboard/work-logs', icon: Activity },", "")
content = content.replace("{ name: 'Контроль', href: '/dashboard/attendance', icon: ClipboardCheck },", "")

# Add single 'Смены' for Admin/Owner/Curator
new_admin_link = "{ name: 'Смены', href: '/dashboard/shifts', icon: ClipboardCheck },"

# I need to insert it correctly. Let's look for `name: 'Кандидаты'` and insert before it for admins.
if "{ name: 'Смены', href: '/dashboard/shifts'" not in content:
    content = content.replace("{ name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },", new_admin_link + "\n        { name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },")

with open('frontend/src/app/dashboard/layout.tsx', 'w') as f:
    f.write(content)
