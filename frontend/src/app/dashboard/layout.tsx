'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, Users, Briefcase, 
  Settings, LogOut, DollarSign, CheckSquare, 
  FileBarChart, MessageSquare, Shield, Activity
} from 'lucide-react';

const getNavigation = (role: string) => {
  const base = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Сообщения', href: '/dashboard/messages', icon: MessageSquare },
  ];

  if (role === 'OWNER') {
    return [
      ...base,
      { name: 'Кураторы', href: '/dashboard/curators', icon: Shield },
      { name: 'Администраторы', href: '/dashboard/admins', icon: Users },
      { name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },
      { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
      { name: 'Партнеры', href: '/dashboard/partners', icon: Briefcase },
      { name: 'Финансы', href: '/dashboard/finance', icon: DollarSign },
      { name: 'Задачи', href: '/dashboard/tasks', icon: CheckSquare },
      { name: 'Отчеты', href: '/dashboard/reports', icon: FileBarChart },
      { name: 'Аналитика', href: '/dashboard/analytics', icon: FileBarChart },
      { name: 'Логи', href: '/dashboard/logs', icon: Activity },
      { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
    ];
  }
  
  if (role === 'CURATOR') {
    return [
      ...base,
      { name: 'Администраторы', href: '/dashboard/admins', icon: Users },
      { name: 'Кандидаты', href: '/dashboard/candidates', icon: Users },
      { name: 'Работники', href: '/dashboard/workers', icon: Briefcase },
      { name: 'Задачи', href: '/dashboard/tasks', icon: CheckSquare },
      { name: 'Отчеты', href: '/dashboard/reports', icon: FileBarChart },
      { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
    ];
  }

  if (role === 'ADMIN') {
    return [
      ...base,
      { name: 'Мои Кандидаты', href: '/dashboard/candidates', icon: Users },
      { name: 'Мои Работники', href: '/dashboard/workers', icon: Briefcase },
      { name: 'Задачи', href: '/dashboard/tasks', icon: CheckSquare },
      { name: 'Отчеты', href: '/dashboard/reports', icon: FileBarChart },
      { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
    ];
  }

  if (role === 'FINANCE') {
    return [
      ...base,
      { name: 'Финансы', href: '/dashboard/finance', icon: DollarSign },
      { name: 'Партнеры', href: '/dashboard/partners', icon: Briefcase },
      { name: 'Отчеты', href: '/dashboard/reports', icon: FileBarChart },
      { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
    ];
  }

  return base;
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!user) return;
    const fetchUnread = async () => {
      try {
        const { data } = await api.get('/messages/');
        const count = data.filter((m: any) => m.receiver_id === user.id && !m.is_read).length;
        setUnreadCount(count);
      } catch (err) {}
    };
    fetchUnread();
    
    // Poll every 10 seconds for new messages
    const interval = setInterval(fetchUnread, 10000);
    return () => clearInterval(interval);
  }, [user]);

  if (!user) return null;

  const navigation = getNavigation(user.role);

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-[#0f172a] text-slate-300 border-r border-slate-800 flex flex-col shadow-2xl z-10 relative">
        <div className="h-16 flex items-center px-6 border-b border-slate-800">
          <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center mr-3 shadow-lg shadow-indigo-500/30">
            <span className="text-white font-bold text-lg">L</span>
          </div>
          <span className="text-xl font-bold text-white tracking-wide">Luneria</span>
        </div>
        
        <div className="flex-1 overflow-y-auto py-6">
          <nav className="space-y-1 px-3">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              const isMessages = item.href === '/dashboard/messages';
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all ${isActive ? 'bg-indigo-500/10 text-indigo-400 border-l-2 border-indigo-500' : 'text-slate-400 hover:text-white hover:bg-slate-800/50'}`}
                >
                  <item.icon className={`mr-3 flex-shrink-0 h-5 w-5 ${isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-white'}`} />
                  <span className="flex-1">{item.name}</span>
                  {isMessages && unreadCount > 0 && (
                    <span className="bg-indigo-600 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                      {unreadCount}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center">
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700">
                {user.name} <span className="text-gray-400 font-normal">#{user.id}</span>
              </p>
              <p className="text-xs font-medium text-gray-500">{user.role}</p>
            </div>
            <button 
              onClick={logout}
              className="ml-auto text-slate-500 hover:text-white transition-colors"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-6 justify-between">
          <h1 className="text-lg font-medium text-gray-900">
            {navigation.find(n => n.href === pathname)?.name || 'Dashboard'}
          </h1>
          {/* Notifications can go here */}
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
