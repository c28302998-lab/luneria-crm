import re

with open("src/app/dashboard/layout.tsx", "r") as f:
    content = f.read()

nav_replacement = """const getNavigation = (role: string) => {
  const base = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Telegram', href: '/dashboard/telegram', icon: MessageCircle },
    { name: 'Сообщения', href: '/dashboard/messages', icon: MessageSquare },
  ];

  if (role === 'OWNER') {
    return [
      { group: 'Главное', items: base },
      { group: 'Команда', items: [
        { name: 'Администраторы', href: '/dashboard/admins', icon: Users },
        { name: 'Кураторы', href: '/dashboard/curators', icon: Shield },
        { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
      ]},
      { group: 'Рекрутинг', items: [
        { name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },
        { name: 'Источники', href: '/dashboard/sources', icon: Globe },
        { name: 'Обучение', href: '/dashboard/training', icon: GraduationCap },
      ]},
      { group: 'Доступы', items: [
        { name: 'Заявки на аккаунт', href: '/dashboard/account-requests', icon: Key },
        { name: 'Аккаунты (OnlyFans)', href: '/dashboard/accounts', icon: Key },
        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },
      ]},
      { group: 'Отчеты и Финансы', items: [
        { name: 'Рабочие смены', href: '/dashboard/worker-reports', icon: Clock },
        { name: 'Сводные Отчеты', href: '/dashboard/reports', icon: FileBarChart },
        { name: 'Финансы (Балансы)', href: '/dashboard/finance', icon: DollarSign },
        { name: 'Выплаты Админам', href: '/dashboard/admin-payouts', icon: DollarSign },
        { name: 'Аналитика', href: '/dashboard/analytics', icon: Activity },
      ]},
      { group: 'Управление', items: [
        { name: 'Контроль', href: '/dashboard/attendance', icon: ClipboardCheck },
        { name: 'Партнеры', href: '/dashboard/partners', icon: Briefcase },
        { name: 'Задачи', href: '/dashboard/tasks', icon: CheckSquare },
      ]},
      { group: 'Система', items: [
        { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
        { name: 'Логи', href: '/dashboard/logs', icon: Activity },
      ]}
    ];
  }
  
  if (role === 'CURATOR') {
    return [
      { group: 'Главное', items: base },
      { group: 'Команда', items: [
        { name: 'Администраторы', href: '/dashboard/admins', icon: Users },
        { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
      ]},
      { group: 'Рекрутинг', items: [
        { name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },
        { name: 'Источники', href: '/dashboard/sources', icon: Globe },
        { name: 'Обучение', href: '/dashboard/training', icon: GraduationCap },
      ]},
      { group: 'Отчеты', items: [
        { name: 'Отчеты работников', href: '/dashboard/worker-reports', icon: Clock },
        { name: 'Сводные Отчеты', href: '/dashboard/reports', icon: FileBarChart },
      ]},
      { group: 'Настройки', items: [
        { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
      ]}
    ];
  }

  if (role === 'ADMIN') {
    return [
      { group: 'Главное', items: base },
      { group: 'Моя команда', items: [
        { name: 'Мои Кандидаты', href: '/dashboard/candidates', icon: Users },
        { name: 'Мои Работники', href: '/dashboard/workers', icon: Briefcase },
      ]},
      { group: 'Отчеты', items: [
        { name: 'Отчеты работников', href: '/dashboard/worker-reports', icon: Clock },
        { name: 'Сводные Отчеты', href: '/dashboard/reports', icon: FileBarChart },
      ]},
      { group: 'Финансы', items: [
        { name: 'Мой баланс', href: '/dashboard/my-balance', icon: DollarSign },
        { name: 'Мои Выплаты', href: '/dashboard/admin-payouts', icon: DollarSign },
      ]},
      { group: 'Доступы', items: [
        { name: 'Мои Аккаунты', href: '/dashboard/accounts', icon: Key },
      ]},
      { group: 'Система', items: [
        { name: 'Обучение', href: '/dashboard/training', icon: GraduationCap },
        { name: 'Источники', href: '/dashboard/sources', icon: Globe },
        { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
      ]}
    ];
  }

  if (role === 'FINANCE') {
    return [
      { group: 'Главное', items: base },
      { group: 'Отчеты и Финансы', items: [
        { name: 'Финансы', href: '/dashboard/finance', icon: DollarSign },
        { name: 'Отчеты', href: '/dashboard/reports', icon: FileBarChart },
      ]}
    ];
  }

  if (role === 'WORKER') {
    return [
      { group: 'Мое Рабочее Место', items: [
        { name: 'Дашборд', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Сдать смену', href: '/dashboard/shift-report', icon: CheckSquare },
        { name: 'Мои аккаунты', href: '/dashboard/my-accounts', icon: Key },
      ]},
      { group: 'Коммуникация', items: [
        { name: 'Telegram', href: '/dashboard/telegram', icon: MessageCircle },
        { name: 'Сообщения', href: '/dashboard/messages', icon: MessageSquare },
      ]},
      { group: 'Полезное', items: [
        { name: 'Обучение', href: '/dashboard/training', icon: GraduationCap },
      ]}
    ];
  }

  return [];
};"""

render_replacement = """          <nav className="space-y-4 px-3">
            {navigation.map((group, groupIdx) => (
              <div key={groupIdx}>
                <h3 className="px-3 text-xs font-bold text-pink-400 uppercase tracking-wider mb-2">{group.group}</h3>
                <div className="space-y-1">
                  {group.items.map((item: any) => {
                    const isActive = pathname === item.href;
                    const isMessages = item.href === '/dashboard/messages';
                    return (
                      <Link
                        key={item.name}
                        onClick={() => setIsMobileMenuOpen(false)}
                        href={item.href}
                        className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all group ${isActive ? 'bg-pink-50 text-pink-700 border-l-2 border-pink-500' : 'text-slate-500 hover:text-pink-600 hover:bg-pink-50'}`}
                      >
                        <item.icon className={`mr-3 flex-shrink-0 h-5 w-5 ${isActive ? 'text-pink-600' : 'text-slate-400 group-hover:text-pink-500'}`} />
                        <span className="flex-1">{item.name}</span>
                        {isMessages && unreadCount > 0 && (
                          <span className="bg-pink-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                            {unreadCount}
                          </span>
                        )}
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
"""

# Replace getNavigation
content = re.sub(r'const getNavigation = \(role: string\) => \{.*?return \[\];\n\};', nav_replacement, content, flags=re.DOTALL)

# Replace rendering logic
content = re.sub(r'<nav className="space-y-1 px-3">.*?(?=\{user\?\.role === \'OWNER\')', render_replacement, content, flags=re.DOTALL)

with open("src/app/dashboard/layout.tsx", "w") as f:
    f.write(content)
