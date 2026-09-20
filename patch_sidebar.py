with open('frontend/src/app/dashboard/layout.tsx', 'r') as f:
    content = f.read()

import re

owner_nav_pattern = re.compile(r"if \(role === 'OWNER'\) \{.*?return \[.*?\];.*?\}", re.DOTALL)

new_owner_nav = """if (role === 'OWNER') {
    return [
      { group: 'Главное', items: [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Задачи', href: '/dashboard/tasks', icon: CheckSquare },
        { name: 'Сообщения', href: '/dashboard/messages', icon: MessageSquare },
      ]},
      { group: 'Рабочие Инструменты', items: [
        { name: 'Telegram', href: '/dashboard/telegram', icon: MessageCircle },
        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },
        { name: 'Почтовые Аккаунты', href: '/dashboard/emails', icon: Mail },
        { name: 'Другие Аккаунты', href: '/dashboard/crm-accounts', icon: Users },
      ]},
      { group: 'HR & Команда', items: [
        { name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },
        { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
        { name: 'Администраторы', href: '/dashboard/admins', icon: Shield },
        { name: 'Партнеры', href: '/dashboard/partners', icon: Users },
      ]},
      { group: 'Смены и Контроль', items: [
        { name: 'Одобрение смен', href: '/dashboard/attendance', icon: ClipboardCheck },
        { name: 'Отчеты работников', href: '/dashboard/worker-reports', icon: Clock },
        { name: 'Логи Работы', href: '/dashboard/work-logs', icon: Activity },
      ]},
      { group: 'Финансы', items: [
        { name: 'Финансы (Балансы)', href: '/dashboard/finance', icon: DollarSign },
        { name: 'Штрафы и Премии', href: '/dashboard/balance-requests', icon: DollarSign },
        { name: 'Выплаты Админам', href: '/dashboard/admin-payouts', icon: DollarSign },
      ]},
      { group: 'Система', items: [
        { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
        { name: 'Обучение', href: '/dashboard/training', icon: GraduationCap },
        { name: 'Источники', href: '/dashboard/sources', icon: Globe },
        { name: 'TG Аудит', href: '/dashboard/telegram-audit', icon: ShieldAlert },
      ]}
    ];
  }"""

content = owner_nav_pattern.sub(new_owner_nav, content)

with open('frontend/src/app/dashboard/layout.tsx', 'w') as f:
    f.write(content)
