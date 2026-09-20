'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Loader2, CheckCircle2, Clock, Calendar, Trash2 } from 'lucide-react';
import { useAuth } from '@/store/auth';

export default function AdminShiftsPage() {
  const { user } = useAuth();
  const [shifts, setShifts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'pending' | 'all'>('pending');

  const fetchShifts = async () => {
    try {
      setLoading(true);
      const endpoint = tab === 'pending' ? '/shifts/pending' : '/shifts/all';
      const res = await api.get(endpoint);
      setShifts(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShifts();
  }, [tab]);

  
  const handleApprove = async (shift: any) => {
    let workerAmount = 0;
    let adminAmount = 0;
    
    const baseAmount = shift.stats?.balance || 0;
    
    const workerInput = prompt(`Подтверждение смены #${shift.id}\nЗаработок воркера (изначально ${baseAmount}):`, String(baseAmount * 0.20));
    if (workerInput === null) return;
    workerAmount = parseFloat(workerInput) || 0;
    
    const adminInput = prompt(`Заработок куратора/админа (изначально ${baseAmount}):`, String(baseAmount * 0.05));
    if (adminInput === null) return;
    adminAmount = parseFloat(adminInput) || 0;
    
    try {
      await api.post(`/shifts/${shift.id}/approve`, {
        worker_amount: workerAmount,
        admin_amount: adminAmount
      });
      alert('Смена одобрена');
      fetchShifts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    }
  };

  const handleApproveOLD = async (id: number) => {
    try {
      await api.post(`/shifts/${id}/approve`);
      alert('Смена одобрена');
      fetchShifts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту смену?')) return;
    try {
      await api.delete(`/shifts/${id}`);
      fetchShifts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при удалении');
    }
  };

  if (loading && shifts.length === 0) return <div className="flex p-8 justify-center"><Loader2 className="w-8 h-8 animate-spin" /></div>;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-foreground">Управление сменами</h2>
        <div className="flex bg-muted p-1 rounded-lg">
          <button 
            onClick={() => setTab('pending')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === 'pending' ? 'bg-background shadow text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
          >
            Ожидают проверки
          </button>
          <button 
            onClick={() => setTab('all')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === 'all' ? 'bg-background shadow text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
          >
            Вся история
          </button>
        </div>
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden">
        {shifts.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">Нет смен в этой категории.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">ID / Воркер</th>
                  <th className="px-4 py-3 font-medium">Тип / Статус</th>
                  <th className="px-4 py-3 font-medium">Время</th>
                  <th className="px-4 py-3 font-medium">Отчет</th>
                  <th className="px-4 py-3 font-medium">Действия</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {shifts.map(shift => (
                  <tr key={shift.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-medium text-foreground">Смена #{shift.id}</div>
                      <div className="text-xs text-muted-foreground">Воркер ID: {shift.worker_id}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium">{shift.shift_type === 'DAY' ? '🌅 День' : '🌙 Ночь'}</div>
                      <span className={`inline-flex px-2 py-1 mt-1 rounded-full text-xs font-medium ${shift.status === 'PENDING_REVIEW' ? 'bg-yellow-100 text-yellow-800' : shift.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                        {shift.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground text-xs">
                      <div>Начало: {new Date(shift.start_time).toLocaleString()}</div>
                      {shift.end_time && <div>Конец: {new Date(shift.end_time).toLocaleString()}</div>}
                    </td>
                    <td className="px-4 py-3">
                      {shift.report_data ? (
                        <div className="text-xs space-y-1">
                          {shift.report_data.screenshot && (
                            <a href={shift.report_data.screenshot} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline flex items-center">
                              <Calendar className="w-3 h-3 mr-1" /> Скриншот
                            </a>
                          )}
                          {shift.stats?.balance && <div>Баланс: <span className="font-medium text-green-600">${shift.stats.balance}</span></div>}
                          {shift.report_data.notes && <div className="text-muted-foreground italic truncate max-w-[200px]">{shift.report_data.notes}</div>}
                        </div>
                      ) : (
                        <span className="text-muted-foreground italic text-xs">Нет отчета</span>
                      )}
                    </td>
                    <td className="px-4 py-3 flex gap-2">
                      {shift.status === 'PENDING_REVIEW' && (
                        <button onClick={() => handleApprove(shift)} className="flex items-center px-3 py-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-xs font-medium">
                          <CheckCircle2 className="w-4 h-4 mr-1" /> Одобрить
                        </button>
                      )}
                      <button onClick={() => handleDelete(shift.id)} className="flex items-center px-3 py-1.5 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors text-xs font-medium" title="Удалить смену">
                        <Trash2 className="w-4 h-4" />
                      </button>
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
