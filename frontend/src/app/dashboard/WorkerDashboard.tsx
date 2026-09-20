import { DollarSign, CheckSquare, GraduationCap, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '@/store/auth';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export default function WorkerDashboard({ balance }: { balance: number }) {
  const { user } = useAuth();
  const [reports, setReports] = useState<any[]>([]);
  const [shiftStatus, setShiftStatus] = useState<any>(null); // {status: string, is_present: bool}
  const [loadingShift, setLoadingShift] = useState(false);

  const loadStatus = () => {
    api.get('/attendance/today-status').then(({data}) => setShiftStatus(data)).catch(console.error);
  };

  useEffect(() => {
    api.get('/shift-reports/').then(({data}) => setReports(data)).catch(console.error);
    loadStatus();
  }, []);

  const handleStartShift = async () => {
    try {
      setLoadingShift(true);
      await api.post('/attendance/start-shift');
      loadStatus();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при начале смены');
    } finally {
      setLoadingShift(false);
    }
  };
  
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-foreground">Привет, {user?.name}!</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-pink-500 to-purple-600 rounded-2xl shadow-lg p-8 text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-20 rounded-full blur-3xl -mr-10 -mt-10"></div>
          <div className="relative z-10">
            <div className="flex items-center mb-6 text-pink-100">
              <DollarSign className="w-6 h-6 mr-2" />
              <h3 className="text-lg font-bold">Баланс</h3>
            </div>
            <div className="text-5xl font-extrabold tracking-tight mb-2">
              ${balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-pink-100 text-sm mt-4">
              Ваш подтвержденный заработок.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          
          {((!shiftStatus) || ['NOT_STARTED', 'NO_WORKER', 'NO_CANDIDATE'].includes(shiftStatus?.status)) && (
            <button onClick={handleStartShift} disabled={loadingShift} className="col-span-2 bg-blue-500 text-white border border-blue-600 p-6 rounded-2xl flex flex-col items-center justify-center text-center hover:bg-blue-600 transition-colors disabled:opacity-50">
              <Clock className="w-10 h-10 mb-3" />
              <h4 className="font-semibold">Начать смену</h4>
              <p className="text-xs mt-1 opacity-80">Отметиться на рабочем месте</p>
            </button>
          )}

          {shiftStatus?.status === 'PENDING' && (
            <div className="col-span-2 bg-yellow-100 text-yellow-800 border border-yellow-200 p-6 rounded-2xl flex flex-col items-center justify-center text-center">
              <Clock className="w-10 h-10 mb-3 animate-pulse" />
              <h4 className="font-semibold">Ожидание подтверждения</h4>
              <p className="text-xs mt-1 opacity-80">Админ скоро проверит вашу отметку</p>
            </div>
          )}

          {shiftStatus?.status === 'APPROVED' && shiftStatus?.is_present && (
            <div className="col-span-2 bg-green-100 text-green-800 border border-green-200 p-6 rounded-2xl flex flex-col items-center justify-center text-center">
              <CheckCircle className="w-10 h-10 mb-3" />
              <h4 className="font-semibold">Смена активна</h4>
              <p className="text-xs mt-1 opacity-80">Админ подтвердил ваш выход</p>
            </div>
          )}

          {shiftStatus?.status === 'REJECTED' && (
            <div className="col-span-2 bg-red-100 text-red-800 border border-red-200 p-6 rounded-2xl flex flex-col items-center justify-center text-center">
              <XCircle className="w-10 h-10 mb-3" />
              <h4 className="font-semibold">Смена отклонена</h4>
              <p className="text-xs mt-1 opacity-80">Админ не подтвердил ваш выход</p>
            </div>
          )}

          <Link href="/dashboard/shift-report" className="bg-card border border-border p-6 rounded-2xl flex flex-col items-center justify-center text-center hover:bg-muted transition-colors">
            <CheckSquare className="w-8 h-8 text-pink-500 mb-2" />
            <h4 className="font-semibold text-foreground">Отчет</h4>
          </Link>
          <Link href="/dashboard/training" className="bg-card border border-border p-6 rounded-2xl flex flex-col items-center justify-center text-center hover:bg-muted transition-colors">
            <GraduationCap className="w-8 h-8 text-purple-500 mb-2" />
            <h4 className="font-semibold text-foreground">Обучение</h4>
          </Link>
        </div>
      </div>
      
      <div className="bg-card rounded-2xl shadow-sm border border-border p-6 mt-8">
        <h3 className="text-xl font-bold mb-4">История отчетов</h3>
        <div className="space-y-3">
          {reports.length === 0 ? <p className="text-muted-foreground text-sm">Отчетов пока нет</p> : null}
          {reports.map((r) => (
            <div key={r.id} className="flex justify-between items-center p-3 bg-muted rounded-lg border border-border">
              <div>
                <div className="font-semibold text-sm">Отчет #{r.id}</div>
                <div className="text-xs text-muted-foreground">{new Date(r.created_at).toLocaleString('ru-RU')}</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="font-bold">${r.amount}</div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${r.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  {r.status === 'APPROVED' ? 'Одобрен' : 'В ожидании'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
