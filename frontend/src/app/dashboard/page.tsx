'use client';

import { useAuth } from '@/store/auth';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Clock } from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    candidates: 0,
    inTraining: 0,
    workers: 0,
    tasks: 0,
    todayCandidates: 0,
    monthCandidates: 0,
    todayWorkers: 0,
    monthWorkers: 0,
    todayRejected: 0,
    monthRejected: 0,
  });
  const [logs, setLogs] = useState<any[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [candRes, workRes, tasksRes, logsRes] = await Promise.all([
          api.get('/candidates/').catch(() => ({ data: [] })),
          api.get('/workers/').catch(() => ({ data: [] })),
          api.get('/tasks/').catch(() => ({ data: [] })),
          api.get('/audit-logs/').catch(() => ({ data: [] }))
        ]);
        const activeCandidates = candRes.data.filter((c: any) => c.status !== 'WORKER');
        
        const now = new Date();
        const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
        const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).getTime();

        const getStats = (items: any[]) => ({
          today: items.filter(i => new Date(i.created_at).getTime() >= todayStart).length,
          month: items.filter(i => new Date(i.created_at).getTime() >= monthStart).length
        });

        const rejectedCandidates = candRes.data.filter((c: any) => c.status === 'REJECTED');

        setStats({
          candidates: activeCandidates.length,
          inTraining: candRes.data.filter((c: any) => c.status === 'IN_PROGRESS').length,
          workers: workRes.data.length,
          tasks: tasksRes.data.length,
          todayCandidates: getStats(candRes.data).today,
          monthCandidates: getStats(candRes.data).month,
          todayWorkers: getStats(workRes.data).today,
          monthWorkers: getStats(workRes.data).month,
          todayRejected: getStats(rejectedCandidates).today,
          monthRejected: getStats(rejectedCandidates).month,
        });
        setLogs(logsRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingLogs(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <p className="text-sm font-medium text-gray-500">Всего кандидатов</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{stats.candidates}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <p className="text-sm font-medium text-gray-500">В обучении (IN_PROGRESS)</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{stats.inTraining}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <p className="text-sm font-medium text-gray-500">Работники</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{stats.workers}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <p className="text-sm font-medium text-gray-500">Задачи</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{stats.tasks}</p>
        </div>
      </div>

      {user?.role === 'ADMIN' && (
        <div className="bg-white shadow-sm border border-gray-100 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-6">Моя статистика</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4 border border-gray-100 p-4 rounded-lg bg-gray-50">
              <h4 className="font-medium text-gray-700 border-b border-gray-200 pb-2">За сегодня</h4>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Добавлено кандидатов:</span>
                <span className="text-sm font-bold text-gray-900">{stats.todayCandidates}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Переведено в работники:</span>
                <span className="text-sm font-bold text-gray-900">{stats.todayWorkers}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Отказов (REJECTED):</span>
                <span className="text-sm font-bold text-gray-900">{stats.todayRejected}</span>
              </div>
            </div>

            <div className="space-y-4 border border-gray-100 p-4 rounded-lg bg-gray-50">
              <h4 className="font-medium text-gray-700 border-b border-gray-200 pb-2">За текущий месяц</h4>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Добавлено кандидатов:</span>
                <span className="text-sm font-bold text-gray-900">{stats.monthCandidates}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Переведено в работники:</span>
                <span className="text-sm font-bold text-gray-900">{stats.monthWorkers}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Отказов (REJECTED):</span>
                <span className="text-sm font-bold text-gray-900">{stats.monthRejected}</span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {user?.role === 'OWNER' && (
        <div className="bg-white shadow-sm border border-gray-100 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-6">Activity Feed (История действий)</h3>
          
          {loadingLogs ? (
            <div className="text-sm text-gray-500">Загрузка истории...</div>
          ) : logs.length === 0 ? (
            <div className="text-sm text-gray-500">История действий пуста.</div>
          ) : (
            <div className="relative border-l border-gray-200 ml-3 space-y-6">
              {logs.slice(0, 20).map((log) => (
                <div key={log.id} className="relative pl-6">
                  <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-indigo-600 border-2 border-white ring-4 ring-white" />
                  <div className="flex justify-between items-start mb-1">
                    <div className="text-sm font-medium text-gray-900">
                      <span className="text-indigo-600 font-bold">{log.action}</span> {log.entity_type} #{log.entity_id}
                    </div>
                    <time className="text-xs text-gray-500 flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {new Date(log.created_at).toLocaleString('ru-RU')}
                    </time>
                  </div>
                  <p className="text-sm text-gray-500">
                    Выполнил Пользователь #{log.user_id}
                  </p>
                  {log.details && Object.keys(log.details).length > 0 && (
                    <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-3 rounded-md border border-gray-100 overflow-x-auto">
                      <pre className="font-mono">{JSON.stringify(log.details, null, 2)}</pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
