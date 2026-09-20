'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Clock, ChevronLeft, ChevronRight } from 'lucide-react';

interface AuditLog {
  id: number;
  user_id: number;
  action: string;
  entity_type: string;
  entity_id: number;
  changes: any;
  created_at: string;
}

export default function LogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const limit = 50;

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const usersRes = await api.get('/users/');
        setUsers(usersRes.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchUsers();
  }, []);

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const skip = (page - 1) * limit;
        const logsRes = await api.get(`/audit-logs/?skip=${skip}&limit=${limit}`);
        setLogs(logsRes.data);
        if (logsRes.data.length < limit) {
          setHasMore(false);
        } else {
          setHasMore(true);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [page]);

  const getUserName = (id: number) => {
    const u = users.find(x => x.id === id);
    return u ? `${u.name} (${u.role})` : `Пользователь #${id}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-foreground">Журнал активности (Логи)</h2>
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="p-2 border border-border rounded-md bg-card disabled:opacity-50"
          >
            <ChevronLeft className="w-5 h-5 text-muted-foreground" />
          </button>
          <span className="text-sm text-muted-foreground font-medium">Страница {page}</span>
          <button 
            onClick={() => setPage(p => p + 1)}
            disabled={!hasMore}
            className="p-2 border border-border rounded-md bg-card disabled:opacity-50"
          >
            <ChevronRight className="w-5 h-5 text-muted-foreground" />
          </button>
        </div>
      </div>

      <div className="bg-card shadow-sm rounded-xl border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Загрузка...</div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">История действий пуста.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-background">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Дата</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Пользователь</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Действие</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Сущность</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Детали (JSON)</th>
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
                {logs.map(log => (
                  <tr key={log.id} className="hover:bg-background">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground flex items-center">
                      <Clock className="w-4 h-4 mr-2 text-gray-400" />
                      {new Date(log.created_at).toLocaleString('ru-RU')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground">
                      {getUserName(log.user_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        log.action === 'CREATE' ? 'bg-green-100 text-green-800' :
                        log.action === 'UPDATE' ? 'bg-blue-100 text-blue-800' :
                        log.action === 'DELETE' ? 'bg-red-100 text-red-800' :
                        'bg-muted text-foreground'
                      }`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {log.entity_type} #{log.entity_id}
                    </td>
                    <td className="px-6 py-4 text-sm text-muted-foreground max-w-xs">
                      {log.changes && Object.keys(log.changes).length > 0 ? (
                        <pre className="text-xs font-mono bg-background p-2 rounded border border-border overflow-x-auto whitespace-pre-wrap">
                          {JSON.stringify(log.changes, null, 2)}
                        </pre>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
