'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { ClipboardCheck, User as UserIcon, Calendar, CheckCircle2, Circle, Clock } from 'lucide-react';
import { useAuth } from '@/store/auth';
import Link from 'next/link';

export default function AttendancePage() {
  const { user } = useAuth();
  const [workers, setWorkers] = useState<any[]>([]);
  const [attendance, setAttendance] = useState<any[]>([]);
  const [candidates, setCandidates] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);
  const [targetDate, setTargetDate] = useState(new Date().toISOString().split('T')[0]); // YYYY-MM-DD

  const fetchData = async () => {
    try {
      setLoading(true);
            const [{ data: wData }, { data: aData }, { data: cData }] = await Promise.all([
        api.get('/workers/'),
        api.get('/attendance/', { params: { target_date: targetDate } }),
        api.get('/candidates/')
      ]);
      
      const cMap: Record<number, string> = {};
      cData.forEach((c: any) => {
        cMap[c.id] = c.first_name || `Кандидат #${c.id}`;
      });
      setCandidates(cMap);

      
      // Filter workers for Admin
      if (user?.role === 'ADMIN') {
        setWorkers(wData.filter((w: any) => w.admin_id === user.id));
      } else {
        setWorkers(wData);
      }
      
      setAttendance(aData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [targetDate, user]);

  const handleIncomeChange = async (workerId: number, value: string, currentPresent: boolean) => {
    if (user?.role !== 'OWNER') return;
    try {
      const val = value === '' ? null : parseFloat(value);
      const res = await api.post('/attendance/', {
        worker_id: workerId,
        date: targetDate,
        is_present: currentPresent,
        income: val
      });
      setAttendance(prev => {
        const existingIdx = prev.findIndex(a => a.worker_id === workerId);
        if (existingIdx >= 0) {
          const newAtt = [...prev];
          newAtt[existingIdx] = res.data;
          return newAtt;
        } else {
          return [...prev, res.data];
        }
      });
    } catch (err) {
      console.error(err);
      alert('Ошибка при сохранении дохода');
    }
  };

  const handleAttendanceToggle = async (workerId: number, currentStatus: boolean, currentIncome?: number) => {
    if (user?.role === 'CURATOR') return; // Cannot edit
    try {
      const res = await api.post('/attendance/', {
        worker_id: workerId,
        date: targetDate,
        is_present: !currentStatus,
        income: currentIncome
      });
      // Update local state
      setAttendance(prev => {
        const existingIdx = prev.findIndex(a => a.worker_id === workerId);
        if (existingIdx >= 0) {
          const newAtt = [...prev];
          newAtt[existingIdx] = res.data;
          return newAtt;
        } else {
          return [...prev, res.data];
        }
      });
    } catch (err) {
      alert('Ошибка при изменении отметки');
    }
  };

  const handleInfoChange = async (workerId: number, field: 'shift' | 'account_info', value: string) => {
    if (user?.role === 'CURATOR') return;
    try {
      await api.patch(`/workers/${workerId}/info`, null, {
        params: { [field]: value }
      });
      setWorkers(prev => prev.map(w => w.id === workerId ? { ...w, [field]: value } : w));
    } catch (err) {
      alert('Ошибка при сохранении данных');
    }
  };

  if (loading && workers.length === 0) return <div className="p-8 text-center text-muted-foreground">Загрузка...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-foreground flex items-center">
            <ClipboardCheck className="w-6 h-6 mr-2 text-primary" />
            Учет рабочего времени
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Отмечайте присутствие работников, их смены и аккаунты.
          </p>
        </div>
        
        <div className="flex items-center space-x-2 bg-card p-2 rounded-lg border border-border shadow-sm">
          <Calendar className="w-4 h-4 text-muted-foreground" />
          <input 
            type="date" 
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            className="text-sm border-none focus:ring-0 text-gray-700 font-medium"
          />
        </div>
      </div>

      <div className="bg-card rounded-xl shadow-sm border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-background">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Работник</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Аккаунт</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Смена (Киев)</th>
                <th className="px-6 py-3 text-center text-xs font-medium text-muted-foreground uppercase tracking-wider">На работе ({targetDate})</th>
              </tr>
            </thead>
            <tbody className="bg-card divide-y divide-border">
              {workers.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-muted-foreground text-sm">
                    Нет привязанных работников
                  </td>
                </tr>
              ) : (
                workers.map(worker => {
                  const att = attendance.find(a => a.worker_id === worker.id);
                  const isPresent = att ? att.is_present : false;
                  const canEdit = user?.role === 'OWNER' || (user?.role === 'ADMIN' && worker.admin_id === user.id);
                  
                  return (
                    <tr key={worker.id} className="hover:bg-background transition">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <UserIcon className="h-8 w-8 text-gray-300 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-foreground">
                              <Link href={`/dashboard/workers/${worker.id}`} className="hover:text-primary">
                                {candidates[worker.candidate_id] || `Работник #${worker.id}`}
                              </Link>
                            </div>
                            {user?.role !== 'ADMIN' && (
                              <div className="text-xs text-muted-foreground">Админ: #{worker.admin_id}</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {canEdit ? (
                          <input 
                            type="text"
                            placeholder="Впишите аккаунт..."
                            value={worker.account_info || ''}
                            onChange={(e) => setWorkers(prev => prev.map(w => w.id === worker.id ? { ...w, account_info: e.target.value } : w))}
                            onBlur={(e) => handleInfoChange(worker.id, 'account_info', e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && e.currentTarget.blur()}
                            className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 w-full"
                          />
                        ) : (
                          <span className="text-sm text-gray-700">{worker.account_info || 'Не указан'}</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {canEdit ? (
                          <input 
                            type="text"
                            placeholder="Напр. 10:00 - 18:00"
                            value={worker.shift || ''}
                            onChange={(e) => setWorkers(prev => prev.map(w => w.id === worker.id ? { ...w, shift: e.target.value } : w))}
                            onBlur={(e) => handleInfoChange(worker.id, 'shift', e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && e.currentTarget.blur()}
                            className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 w-32"
                          />
                        ) : (
                          <span className="text-sm text-gray-700">{worker.shift || 'Не указана'}</span>
                        )}
                      </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                          <button 
                            onClick={() => handleAttendanceToggle(worker.id, isPresent, att?.income)}
                            disabled={!canEdit}
                            className={`focus:outline-none transition-transform active:scale-95 ${!canEdit ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:opacity-80'}`}
                          >
                            {att?.status === 'PENDING' ? (
                              <Clock className="w-8 h-8 text-yellow-500 mx-auto animate-pulse" />
                            ) : isPresent ? (
                              <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto" />
                            ) : (
                              <Circle className="w-8 h-8 text-gray-300 mx-auto hover:text-gray-400" />
                            )}
                          </button>
                          
                          {user?.role === 'OWNER' && (
                            <div className="flex items-center gap-1">
                              <span className="text-muted-foreground text-sm font-medium">$</span>
                              <input
                                type="number"
                                placeholder="Доход"
                                className="w-20 text-sm border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 px-2 py-1"
                                value={att?.income !== undefined && att?.income !== null ? att.income : ''}
                                onChange={(e) => {
                                  const newAtt = [...attendance];
                                  const existingIdx = newAtt.findIndex(a => a.worker_id === worker.id);
                                  if (existingIdx >= 0) newAtt[existingIdx].income = e.target.value === '' ? null : parseFloat(e.target.value);
                                  else newAtt.push({ worker_id: worker.id, is_present: isPresent, income: e.target.value === '' ? null : parseFloat(e.target.value) });
                                  setAttendance(newAtt);
                                }}
                                onBlur={(e) => handleIncomeChange(worker.id, e.target.value, isPresent)}
                              />
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
