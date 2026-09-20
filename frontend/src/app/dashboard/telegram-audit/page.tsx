'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { ShieldAlert, Activity, User, MonitorSmartphone } from 'lucide-react';

export default function TelegramAuditPage() {
  const { user } = useAuth();
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    if (user?.role === 'OWNER') {
      api.get('/telegram/admin/audit').then(res => setLogs(res.data)).catch(console.error);
    }
  }, [user]);

  if (user?.role !== 'OWNER') return <div>Access Denied</div>;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <ShieldAlert className="w-8 h-8 text-red-500" />
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Аудит Telegram</h1>
          <p className="text-sm text-muted-foreground">Журнал всех действий в рабочих аккаунтах</p>
        </div>
      </div>

      <div className="bg-card rounded-xl shadow-sm border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-background">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Дата / Время</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Сотрудник</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Аккаунт</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Действие</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">IP / Детали</th>
              </tr>
            </thead>
            <tbody className="bg-card divide-y divide-border">
              {logs.map((log: any) => (
                <tr key={log.id} className="hover:bg-background">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium text-foreground">{log.user?.username || 'Unknown'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {log.account_id ? (
                      <div className="flex items-center gap-2 text-sm text-foreground">
                        <MonitorSmartphone className="w-4 h-4 text-indigo-400" />
                        Acc #{log.account_id}
                      </div>
                    ) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-700">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground max-w-xs truncate">
                    <div className="font-mono text-xs">{log.ip_address || 'N/A'}</div>
                    <div className="truncate" title={log.details}>{log.details}</div>
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">Нет записей в журнале аудита</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
