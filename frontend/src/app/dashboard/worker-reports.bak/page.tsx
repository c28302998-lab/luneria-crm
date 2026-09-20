'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Check, X } from 'lucide-react';

export default function WorkerReportsPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [amounts, setAmounts] = useState<Record<number, {worker: number, admin: number}>>({});

  const fetchReports = async () => {
    try {
      const { data } = await api.get('/shift-reports/');
      setReports(data);
      const newAmounts: any = {};
      data.forEach((r: any) => {
        newAmounts[r.id] = { worker: r.amount * 0.2, admin: r.amount * 0.05 };
      });
      setAmounts(newAmounts);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  
  const handleDelete = async (id: number) => {
    if (!confirm("Точно удалить этот отчет?")) return;
    try {
      await api.delete(`/shift-reports/${id}`);
      fetchReports();
    } catch (err) {
      alert("Ошибка при удалении");
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await api.put(`/shift-reports/${id}/approve`, {
        worker_amount: amounts[id]?.worker || 0,
        admin_amount: amounts[id]?.admin || 0
      });
      fetchReports();
    } catch (err) {
      alert("Ошибка при подтверждении");
    }
  };

  if (user?.role !== 'OWNER' && user?.role !== 'FINANCE' && user?.role !== 'ADMIN') return null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground">Рабочие смены</h2>
        <p className="text-muted-foreground text-sm mt-1">{user?.role === 'ADMIN' ? 'Здесь вы можете отслеживать отчеты ваших работников для удобного сбора ежедневной статистики по команде.' : 'Здесь вы проверяете и утверждаете отчеты о заработке от ваших работников. После подтверждения баланс автоматически начисляется.'}</p>
      </div>
            {user?.role === 'ADMIN' && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gradient-to-br from-pink-500 to-purple-600 rounded-xl p-6 text-white shadow-md">
            <h3 className="text-sm font-semibold opacity-90 mb-1">Заработано командой (Сегодня)</h3>
            <div className="text-3xl font-bold">${reports.filter(r => new Date(r.created_at).toDateString() === new Date().toDateString()).reduce((sum, r) => sum + r.amount, 0).toFixed(2)}</div>
          </div>
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-muted-foreground mb-1">Сдано отчетов (Сегодня)</h3>
            <div className="text-3xl font-bold text-foreground">{reports.filter(r => new Date(r.created_at).toDateString() === new Date().toDateString()).length}</div>
          </div>
        </div>
      )}
      <div className="bg-card shadow-sm rounded-xl border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Загрузка...</div>
        ) : reports.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">Нет отчетов</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-background">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Работник</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Ник/Имя</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Сумма</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Скриншоты</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Статус</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Дата</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
                {reports.map(r => (
                  <tr key={r.id}>
                    <td className="px-6 py-4 text-sm text-foreground">#{r.id}</td>
                    <td className="px-6 py-4 text-sm text-foreground">{r.worker_name || `User #${r.worker_id}`}</td>
                    <td className="px-6 py-4 text-sm text-foreground">{r.notes || '-'}</td>
                    <td className="px-6 py-4 text-sm font-bold text-green-500">${r.amount}</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">
                      {r.files && r.files.length > 0 ? (
                        <a href={r.files[0]} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">
                          Скриншот
                        </a>
                      ) : (
                        "Нет"
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        r.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">{new Date(r.created_at).toLocaleString('ru-RU')}</td>
                    <td className="px-6 py-4 text-right">
                      {r.status === 'APPROVED' && (
                        <div className="flex flex-col items-end gap-1 text-xs text-muted-foreground">
                          <div>Работнику: <span className="font-medium text-green-600">${r.worker_amount || 0}</span></div>
                          <div>Админу {r.admin_name ? `(${r.admin_name})` : ''}: <span className="font-medium text-blue-600">${r.admin_amount || 0}</span></div>
                        </div>
                      )}
                      {r.status === 'PENDING' && (user?.role === 'OWNER' || user?.role === 'FINANCE') && (
                        <div className="flex flex-col gap-2 items-end">
                          <div className="flex items-center gap-2 text-xs text-slate-500">
                            <span>Работнику: $</span>
                            <input type="number" className="w-16 border rounded px-1" value={amounts[r.id]?.worker || ''} onChange={(e) => setAmounts({...amounts, [r.id]: {...amounts[r.id], worker: Number(e.target.value)}})} />
                          </div>
                          <div className="flex items-center gap-2 text-xs text-slate-500">
                            <span>Админу {r.admin_name ? `(${r.admin_name})` : ''}: $</span>
                            <input type="number" className="w-16 border rounded px-1" value={amounts[r.id]?.admin || ''} onChange={(e) => setAmounts({...amounts, [r.id]: {...amounts[r.id], admin: Number(e.target.value)}})} />
                          </div>
                          <div className="flex justify-end gap-3 mt-1">
                            <button 
                              onClick={() => handleDelete(r.id)}
                              className="text-red-500 hover:text-red-700 flex items-center text-xs"
                            >
                              <X className="h-4 w-4 mr-1" /> Удалить
                            </button>
                            <button 
                              onClick={() => handleApprove(r.id)}
                              className="text-green-600 hover:text-green-800 flex items-center text-xs"
                            >
                              <Check className="h-4 w-4 mr-1" /> Подтвердить
                            </button>
                          </div>
                        </div>
                      )}
                      {r.status === 'PENDING' && user?.role === 'ADMIN' && (
                        <span className="text-xs text-muted-foreground italic">Ожидает Овнера</span>
                      )}
                      {r.status !== 'PENDING' && (user?.role === 'OWNER' || user?.role === 'FINANCE') && (
                        <button 
                          onClick={() => handleDelete(r.id)}
                          className="text-red-500 hover:text-red-700 flex items-center justify-end w-full text-xs mt-2"
                        >
                          <X className="h-3 w-3 mr-1" /> Удалить
                        </button>
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
