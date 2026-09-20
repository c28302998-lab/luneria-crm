with open("frontend/src/app/dashboard/layout.tsx", "r") as f:
    content = f.read()

import re

old_team = """      { group: 'Команда', items: [
        { name: 'Администраторы', href: '/dashboard/admins', icon: Users },
        { name: 'Кураторы', href: '/dashboard/curators', icon: Shield },
        { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
      ]},"""

new_team = """      { group: 'Команда', items: [
        { name: 'Администраторы', href: '/dashboard/admins', icon: Users },
        { name: 'Кураторы', href: '/dashboard/curators', icon: Shield },
        { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
        { name: 'Логи Работы', href: '/dashboard/work-logs', icon: Activity },
      ]},"""

content = content.replace(old_team, new_team)

with open("frontend/src/app/dashboard/layout.tsx", "w") as f:
    f.write(content)
