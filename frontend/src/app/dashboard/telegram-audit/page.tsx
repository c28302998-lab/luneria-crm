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
          <h1 className="text-2xl font-semibold text-gray-900">Аудит Telegram</h1>
          <p className="text-sm text-gray-500">Журнал всех действий в рабочих аккаунтах</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата / Время</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Сотрудник</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Аккаунт</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Действие</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP / Детали</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log: any) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-900">{log.user?.username || 'Unknown'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {log.account_id ? (
                      <div className="flex items-center gap-2 text-sm text-gray-900">
                        <MonitorSmartphone className="w-4 h-4 text-indigo-400" />
                        Acc #{log.account_id}
                      </div>
                    ) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-50 text-blue-700">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                    <div className="font-mono text-xs">{log.ip_address || 'N/A'}</div>
                    <div className="truncate" title={log.details}>{log.details}</div>
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">Нет записей в журнале аудита</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
