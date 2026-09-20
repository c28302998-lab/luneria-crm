'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, Users, Briefcase, 
  Settings, LogOut, DollarSign, CheckSquare, 
  FileBarChart, MessageSquare, Mail, Shield, Activity, Bell
, GraduationCap, Globe, Key, Menu, X , MessageCircle, ShieldAlert, MonitorSmartphone } from 'lucide-react';
import { ClipboardCheck, Clock, Moon } from 'lucide-react';
import ShiftButton from '@/components/ShiftButton';

const getNavigation = (role: string) => {
  const base = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Telegram', href: '/dashboard/telegram', icon: MessageCircle },
    { name: 'Почты', href: '/dashboard/emails', icon: Mail },
    { name: 'Сообщения', href: '/dashboard/messages', icon: MessageSquare },
  ];

  if (role === 'OWNER') {
    return [
      { group: 'Главное', items: [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Задачи', href: '/dashboard/tasks', icon: CheckSquare },
        { name: 'Сообщения', href: '/dashboard/messages', icon: MessageSquare },
      ]},
      { group: 'Рабочие Инструменты', items: [
        { name: 'Telegram', href: '/dashboard/telegram', icon: MessageCircle },
        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },
        { name: 'Ревью Аккаунтов', href: '/dashboard/reviews', icon: CheckSquare },
        { name: 'Почтовые Аккаунты', href: '/dashboard/emails', icon: Mail },
        { name: 'Другие Аккаунты', href: '/dashboard/crm-accounts', icon: Users },
      ]},
      { group: 'HR & Команда', items: [
        { name: 'Смены', href: '/dashboard/shifts', icon: ClipboardCheck },
        { name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },
        { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
        { name: 'Администраторы', href: '/dashboard/admins', icon: Shield },
        { name: 'Партнеры', href: '/dashboard/partners', icon: Users },
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
  }
  
  if (role === 'CURATOR') {
    return [
      { group: 'Главное', items: base },
      { group: 'Команда', items: [
        { name: 'Администраторы', href: '/dashboard/admins', icon: Users },
        { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
        
      ]},
      { group: 'Рекрутинг', items: [
        { name: 'Смены', href: '/dashboard/shifts', icon: ClipboardCheck },
        { name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },
        { name: 'Источники', href: '/dashboard/sources', icon: Globe },
        { name: 'Обучение', href: '/dashboard/training', icon: GraduationCap },
      ]},
      { group: 'Отчеты', items: [
        
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
        
        { name: 'Сводные Отчеты', href: '/dashboard/reports', icon: FileBarChart },
      ]},
      { group: 'Финансы', items: [
        { name: 'Мой баланс', href: '/dashboard/my-balance', icon: DollarSign },
        { name: 'Мои Выплаты', href: '/dashboard/admin-payouts', icon: DollarSign },
      ]},
      { group: 'Доступы', items: [
        { name: 'TG Аккаунты', href: '/dashboard/telegram-accounts', icon: MonitorSmartphone },
        { name: 'Ревью Аккаунтов', href: '/dashboard/reviews', icon: CheckSquare },
      ]},
      { group: 'Управление', items: [
        { name: 'Задачи', href: '/dashboard/tasks', icon: CheckSquare },
      ]},
      { group: 'Система', items: [
        { name: 'Обучение', href: '/dashboard/training', icon: GraduationCap },
        { name: 'Источники', href: '/dashboard/sources', icon: Globe },
        { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
      ]},
    ];
  }

  if (role === 'FINANCE') {
    return [
      { group: 'Главное', items: base },
      { group: 'Отчеты и Финансы', items: [
        { name: 'Финансы', href: '/dashboard/finance', icon: DollarSign },
        { name: 'Отчеты', href: '/dashboard/reports', icon: FileBarChart },
        { name: 'Выплаты Админам', href: '/dashboard/admin-payouts', icon: DollarSign },
      ]}
    ];
  }

  if (role === 'WORKER') {
    return [
      { group: 'Мое Рабочее Место', items: [
        { name: 'Дашборд', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Мои Смены', href: '/dashboard/my-shifts', icon: Clock },
        { name: 'Мои аккаунты (TG)', href: '/dashboard/my-accounts', icon: Key },
        { name: 'Почты', href: '/dashboard/emails', icon: Mail },
      ]},
      { group: 'Коммуникация', items: [
        { name: 'Сообщения', href: '/dashboard/messages', icon: MessageSquare },
      ]}
    ];
  }

  return [{ group: 'Меню', items: base }];
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (!user) return;

    const fetchUnread = async () => {
      try {
        const { data } = await api.get('/messages/');
        const count = data.filter((m: any) => m.receiver_id === user.id && !m.is_read).length;
        setUnreadCount(count);
      } catch (err) {}
    };
    
    const fetchNotifications = async () => {
      try {
        const { data } = await api.get('/notifications/');
        setNotifications(data);
      } catch (err) {}
    };

    fetchUnread();

    // TEMPORARY FIX: auto-call fix endpoint
    if (user?.role === 'OWNER') {
      api.get('/workers/tools/fix-deleted-users').catch(() => {});
    }

    fetchNotifications();
    
    // Poll every 10 seconds for new messages
    const interval = setInterval(() => {
      fetchUnread();

    // TEMPORARY FIX: auto-call fix endpoint
    if (user?.role === 'OWNER') {
      api.get('/workers/tools/fix-deleted-users').catch(() => {});
    }

      fetchNotifications();
    }, 10000);

    return () => clearInterval(interval);
  }, [user]);


  const markNotificationRead = async (id: number) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch(err) {}
  };

  if (!user) return null;

  const navigation = getNavigation(user.role);

  return (
    <div className="flex h-screen bg-muted">
      {/* Mobile Sidebar Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden" 
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 transform ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 w-64 bg-white text-slate-600 border-r border-pink-100 flex flex-col shadow-sm z-50 transition-transform duration-300 ease-in-out`}>
        <div className="h-16 flex items-center px-6 border-b border-pink-100">
          <div className="w-10 h-10 rounded-full flex items-center justify-center mr-3 overflow-hidden bg-transparent">
            <img src="/logo.png" alt="Lunery Logo" className="w-full h-full object-cover" />
          </div>
          <span className="text-xl font-bold text-slate-900 tracking-wide">{process.env.NEXT_PUBLIC_AGENCY_NAME ? process.env.NEXT_PUBLIC_AGENCY_NAME + " CRM" : "Lunery CRM"}</span>
        </div>
        
        <div className="flex-1 overflow-y-auto py-6">
                    <nav className="space-y-4 px-3">
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
{user?.role === 'OWNER' && (
              <Link
                href="/dashboard/referrals"
                className={`flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  pathname === '/dashboard/referrals'
                    ? 'bg-primary/10 text-indigo-700'
                    : 'text-muted-foreground hover:bg-background hover:text-foreground'
                }`}
              >
                <Users className="w-5 h-5 mr-3" />
                Рефералы
              </Link>
            )}
          </nav>
        </div>

        <div className="border-t border-slate-700 p-4 mt-auto">
          <div className="flex items-center">
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700">
                {user.name} <span className="text-gray-400 font-normal">#{user.id}</span>
              </p>
              <p className="text-xs font-medium text-muted-foreground">{user.role}</p>
            </div>
            <button 
              onClick={logout}
              className="ml-auto text-muted-foreground hover:text-white transition-colors"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-card border-b border-border flex items-center px-4 md:px-6 justify-between shrink-0">
          <div className="flex items-center gap-3">
            <button 
              className="p-2 md:hidden text-muted-foreground hover:text-foreground focus:outline-none" 
              onClick={() => setIsMobileMenuOpen(true)}
            >
              <Menu className="w-6 h-6" />
            </button>
            <h1 className="text-lg font-medium text-foreground truncate max-w-[150px] sm:max-w-xs">
              {navigation.flatMap(g => g.items).find(n => n.href === pathname)?.name || 'Dashboard'}
            </h1>
          </div>
          
          <div className="flex items-center gap-2 md:gap-4">
            <div className="hidden sm:block">
              <ShiftButton />
            </div>
          <div className="relative">
            <button 
              onClick={() => setIsNotifOpen(!isNotifOpen)}
              className="p-2 text-gray-400 hover:text-muted-foreground relative"
            >
              <Bell className="w-6 h-6" />
              {notifications.filter(n => !n.is_read).length > 0 && (
                <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500/100 border-2 border-white rounded-full"></span>
              )}
            </button>
            
            {isNotifOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-card rounded-xl shadow-lg border border-border py-2 z-50 max-h-[400px] overflow-y-auto">
                <h3 className="px-4 py-2 font-semibold text-foreground border-b border-border">Уведомления</h3>
                {notifications.length === 0 ? (
                  <div className="p-4 text-center text-sm text-muted-foreground">Нет новых уведомлений</div>
                ) : (
                  notifications.map(n => (
                    <div 
                      key={n.id} 
                      onClick={() => markNotificationRead(n.id)}
                      className={`px-4 py-3 hover:bg-background cursor-pointer border-b border-border last:border-0 ${!n.is_read ? 'bg-primary/10/50' : 'opacity-70'}`}
                    >
                      <h4 className={`text-sm font-medium ${!n.is_read ? 'text-indigo-900' : 'text-foreground'}`}>{n.type}</h4>
                      <p className="text-xs text-muted-foreground mt-1">{n.message}</p>
                      <span className="text-[10px] text-gray-400 mt-2 block">{new Date(n.created_at).toLocaleString('ru-RU')}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
