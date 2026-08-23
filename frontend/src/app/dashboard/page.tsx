'use client';

import { useAuth } from '@/store/auth';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import * as XLSX from 'xlsx';
import { Clock, Users, Briefcase, CheckCircle, TrendingUp, DollarSign, Activity } from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();
  const [rawData, setRawData] = useState<any>(null);
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
  const [finances, setFinances] = useState({ revenue: 0, payouts: 0 });
  const [logs, setLogs] = useState<any[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(true);

  const generateExcelReport = () => {
    if (!rawData) return;
    const wb = XLSX.utils.book_new();

    // 1. Finances
    const finStats = rawData.payments;
    const finWs = XLSX.utils.json_to_sheet([
      { "Показатель": "Выручка компании", "Сумма ($)": finStats.company_revenue || 0 },
      { "Показатель": "Ожидаемые выплаты", "Сумма ($)": (finStats.worker_revenue || 0) + (finStats.admin_revenue || 0) },
      { "Показатель": "Расходы (Расстраты)", "Сумма ($)": finStats.total_expenses || 0 },
      { "Показатель": "Чистая прибыль", "Сумма ($)": finStats.net_profit || 0 }
    ]);
    XLSX.utils.book_append_sheet(wb, finWs, "Финансы");

    // 2. Candidates
    const candWs = XLSX.utils.json_to_sheet(rawData.candidates.map((c: any) => ({
      "ID": c.id,
      "Имя": c.name,
      "Контакты": c.contact_info,
      "Статус": c.status,
      "Дата регистрации": new Date(c.created_at).toLocaleDateString()
    })));
    XLSX.utils.book_append_sheet(wb, candWs, "Кандидаты");

    // 3. Workers
    const workWs = XLSX.utils.json_to_sheet(rawData.workers.map((w: any) => ({
      "ID": w.id,
      "Имя": w.user?.full_name || 'Без имени',
      "Специализация": w.specialization,
      "Доля (%)": w.share_percentage
    })));
    XLSX.utils.book_append_sheet(wb, workWs, "Работники");

    // 4. Tasks
    const taskWs = XLSX.utils.json_to_sheet(rawData.tasks.map((t: any) => ({
      "ID": t.id,
      "Название": t.title,
      "Приоритет": t.priority,
      "Статус": t.status
    })));
    XLSX.utils.book_append_sheet(wb, taskWs, "Задачи");

    XLSX.writeFile(wb, `Luneria_Report_${new Date().toISOString().split('T')[0]}.xlsx`);
  };


  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [candRes, workRes, tasksRes, logsRes, statsFinRes] = await Promise.all([
          api.get('/candidates/').catch(() => ({ data: [] })),
          api.get('/workers/').catch(() => ({ data: [] })),
          api.get('/tasks/').catch(() => ({ data: [] })),
          api.get('/audit-logs/').catch(() => ({ data: [] })),
          api.get('/payments/stats').catch(() => ({ data: { company_revenue: 0, net_profit: 0, worker_revenue: 0, admin_revenue: 0 } }))
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

        
        
        const revenue = statsFinRes.data.net_profit || statsFinRes.data.company_revenue || 0;
        const payouts = (statsFinRes.data.worker_revenue || 0) + (statsFinRes.data.admin_revenue || 0);
        setFinances({ revenue, payouts });

        setRawData({ candidates: candRes.data, workers: workRes.data, tasks: tasksRes.data, payments: statsFinRes.data });
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
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Header section with greeting */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-indigo-500 opacity-5 rounded-full blur-3xl"></div>
        <div>
          <h2 className="text-2xl font-bold text-slate-800">С возвращением, {user?.name}! 👋</h2>
          <p className="text-slate-500 mt-1">Вот краткая сводка по вашим показателям на сегодня.</p>
        </div>
        <div className="flex space-x-3">
          <div className="px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-medium border border-indigo-100 flex items-center">
            <span className="w-2 h-2 rounded-full bg-indigo-500 mr-2 animate-pulse"></span>
            Роль: {user?.role}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col justify-between hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-50 rounded-full transition-transform group-hover:scale-110"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
            </div>
            <p className="text-sm font-medium text-slate-500">Всего кандидатов</p>
            <p className="mt-1 text-3xl font-bold text-slate-800">{stats.candidates}</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col justify-between hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-amber-50 rounded-full transition-transform group-hover:scale-110"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center">
                <Activity className="w-5 h-5" />
              </div>
            </div>
            <p className="text-sm font-medium text-slate-500">В обучении</p>
            <p className="mt-1 text-3xl font-bold text-slate-800">{stats.inTraining}</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col justify-between hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-emerald-50 rounded-full transition-transform group-hover:scale-110"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
                <Briefcase className="w-5 h-5" />
              </div>
            </div>
            <p className="text-sm font-medium text-slate-500">Активные работники</p>
            <p className="mt-1 text-3xl font-bold text-slate-800">{stats.workers}</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col justify-between hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-purple-50 rounded-full transition-transform group-hover:scale-110"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center">
                <CheckCircle className="w-5 h-5" />
              </div>
            </div>
            <p className="text-sm font-medium text-slate-500">Задачи</p>
            <p className="mt-1 text-3xl font-bold text-slate-800">{stats.tasks}</p>
          </div>
        </div>
      </div>
      {user?.role === 'ADMIN' && (
        <div className="bg-white shadow-sm border border-slate-100 rounded-2xl p-6">
          <div className="flex items-center mb-6">
            <TrendingUp className="w-5 h-5 text-indigo-500 mr-2" />
            <h3 className="text-lg font-bold text-slate-800">Эффективность рекрутинга</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4 border border-slate-100 p-5 rounded-xl bg-slate-50 relative overflow-hidden">
              <div className="absolute right-0 bottom-0 opacity-10">
                 <Clock className="w-24 h-24 -mb-4 -mr-4 text-slate-400" />
              </div>
              <h4 className="font-bold text-slate-700 border-b border-slate-200 pb-3 uppercase text-xs tracking-wider">За сегодня</h4>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span className="text-sm text-slate-500 font-medium">Кандидатов:</span>
                <span className="text-lg font-bold text-indigo-600">{stats.todayCandidates}</span>
              </div>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span className="text-sm text-slate-500 font-medium">Переведено в работники:</span>
                <span className="text-lg font-bold text-emerald-600">{stats.todayWorkers}</span>
              </div>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span className="text-sm text-slate-500 font-medium">Отказов:</span>
                <span className="text-lg font-bold text-red-500">{stats.todayRejected}</span>
              </div>
            </div>

            <div className="space-y-4 border border-slate-100 p-5 rounded-xl bg-slate-50 relative overflow-hidden">
               <div className="absolute right-0 bottom-0 opacity-10">
                 <Activity className="w-24 h-24 -mb-4 -mr-4 text-slate-400" />
              </div>
              <h4 className="font-bold text-slate-700 border-b border-slate-200 pb-3 uppercase text-xs tracking-wider">За текущий месяц</h4>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span className="text-sm text-slate-500 font-medium">Кандидатов:</span>
                <span className="text-lg font-bold text-indigo-600">{stats.monthCandidates}</span>
              </div>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span className="text-sm text-slate-500 font-medium">Переведено в работники:</span>
                <span className="text-lg font-bold text-emerald-600">{stats.monthWorkers}</span>
              </div>
              <div className="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                <span className="text-sm text-slate-500 font-medium">Отказов:</span>
                <span className="text-lg font-bold text-red-500">{stats.monthRejected}</span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {(user?.role === 'OWNER' || user?.role === 'FINANCE') && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white shadow-sm border border-slate-100 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Лента активности</h3>
            
            {loadingLogs ? (
              <div className="text-sm text-slate-500">Загрузка истории...</div>
            ) : logs.length === 0 ? (
              <div className="text-sm text-slate-500 bg-slate-50 p-6 rounded-xl text-center border border-dashed border-slate-200">История действий пуста.</div>
            ) : (
              <div className="relative border-l-2 border-indigo-100 ml-4 space-y-6">
                {logs.slice(0, 10).map((log) => (
                  <div key={log.id} className="relative pl-6">
                    <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full bg-indigo-500 border-4 border-white shadow-sm" />
                    <div className="flex justify-between items-start mb-1">
                      <div className="text-sm font-medium text-slate-800">
                        <span className="text-indigo-600 font-bold bg-indigo-50 px-2 py-0.5 rounded-md mr-1">{log.action}</span> 
                        {log.entity_type} #{log.entity_id}
                      </div>
                      <time className="text-xs text-slate-400 flex items-center bg-slate-50 px-2 py-1 rounded-md">
                        <Clock className="w-3 h-3 mr-1" />
                        {new Date(log.created_at).toLocaleString('ru-RU')}
                      </time>
                    </div>
                    <p className="text-sm text-slate-500">
                      Выполнил Пользователь #{log.user_id}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="bg-gradient-to-br from-indigo-900 to-slate-900 rounded-2xl shadow-lg p-6 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500 opacity-20 rounded-full blur-3xl -mr-10 -mt-10"></div>
            <div className="absolute bottom-0 left-0 w-40 h-40 bg-emerald-500 opacity-10 rounded-full blur-3xl -ml-10 -mb-10"></div>
            
            <div className="relative z-10">
              <div className="flex items-center mb-6 text-indigo-300">
                <DollarSign className="w-5 h-5 mr-2" />
                <h3 className="text-lg font-bold">Финансовая сводка</h3>
              </div>
              
              <div className="space-y-6">
                <div>
                  <p className="text-sm text-slate-400 font-medium">Выручка компании</p>
                  <p className="text-3xl font-bold mt-1 text-white flex items-baseline">
                    ${finances.revenue.toLocaleString()}
                    <span className="text-sm text-emerald-400 ml-2 font-medium flex items-center">
                      <TrendingUp className="w-3 h-3 mr-1" /> 
                    </span>
                  </p>
                </div>
                
                <div className="pt-4 border-t border-slate-700/50">
                  <p className="text-sm text-slate-400 font-medium">Ожидаемые выплаты</p>
                  <p className="text-2xl font-bold mt-1 text-white">${finances.payouts.toLocaleString()}</p>
                </div>
                
                <button onClick={generateExcelReport} className="w-full py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl transition font-medium mt-4">
                  Сформировать отчет
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}