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
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <span className="text-xl font-bold text-indigo-600">Luneria</span>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-3">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              const isMessages = item.href === '/dashboard/messages';
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    isActive 
                      ? 'bg-indigo-50 text-indigo-600' 
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <item.icon className={`mr-3 flex-shrink-0 h-5 w-5 ${isActive ? 'text-indigo-600' : 'text-gray-400'}`} />
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
              className="ml-auto text-gray-400 hover:text-gray-500"
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
