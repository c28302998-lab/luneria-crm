'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Loader2, Play, Square, Image as ImageIcon } from 'lucide-react';

export default function MyShiftsPage() {
  const [shifts, setShifts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // End shift form
  const [showEndModal, setShowEndModal] = useState(false);
  const [reportUrl, setReportUrl] = useState('');
  const [balance, setBalance] = useState('');
  const [notes, setNotes] = useState('');

  const fetchShifts = async () => {
    try {
      const res = await api.get('/shifts/my');
      setShifts(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShifts();
  }, []);

  const activeShift = shifts.find(s => s.status === 'ACTIVE');

  const handleStart = async (type: string) => {
    try {
      await api.post('/shifts/start', { shift_type: type });
      fetchShifts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    }
  };

  const handleEnd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/shifts/end', {
        report_data: { screenshot: reportUrl, notes },
        stats: { balance: parseFloat(balance) || 0 }
      });
      setShowEndModal(false);
      setReportUrl('');
      setBalance('');
      setNotes('');
      fetchShifts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    }
  };

  if (loading && shifts.length === 0) return <div className="flex p-8 justify-center"><Loader2 className="w-8 h-8 animate-spin" /></div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-foreground">Моя смена</h2>
      
      <div className="bg-card rounded-xl border border-border p-8 shadow-sm text-center">
        {activeShift ? (
          <div>
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-4 animate-pulse">
              <Play className="w-8 h-8 ml-1" />
            </div>
            <h3 className="text-2xl font-bold mb-2">Смена активна ({activeShift.shift_type === 'DAY' ? 'День' : 'Ночь'})</h3>
            <p className="text-muted-foreground mb-6">Начата: {new Date(activeShift.start_time).toLocaleTimeString()}</p>
            <button 
              onClick={() => setShowEndModal(true)}
              className="px-6 py-3 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 transition shadow-lg shadow-red-200 flex items-center mx-auto"
            >
              <Square className="w-5 h-5 mr-2" />
              Завершить смену и сдать отчет
            </button>
          </div>
        ) : (
          <div>
            <h3 className="text-xl font-bold mb-6">У вас нет активной смены</h3>
            <div className="flex justify-center space-x-4">
              <button 
                onClick={() => handleStart('DAY')}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition flex items-center"
              >
                <Play className="w-5 h-5 mr-2" /> Начать Дневную
              </button>
              <button 
                onClick={() => handleStart('NIGHT')}
                className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition flex items-center"
              >
                <Play className="w-5 h-5 mr-2" /> Начать Ночную
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden mt-8">
        <h3 className="p-6 text-lg font-bold border-b border-border">История смен</h3>
        <div className="divide-y divide-border">
          {shifts.map(shift => (
            <div key={shift.id} className="p-4 flex flex-col sm:flex-row justify-between hover:bg-muted/30 transition">
              <div>
                <span className="font-medium">Смена {shift.shift_type}</span>
                <p className="text-xs text-muted-foreground mt-1">
                  {new Date(shift.start_time).toLocaleString()} — {shift.end_time ? new Date(shift.end_time).toLocaleTimeString() : 'В процессе'}
                </p>
                {shift.stats?.balance && <p className="text-sm font-bold text-green-600 mt-2">Баланс: ${shift.stats.balance}</p>}
              </div>
              <div className="mt-2 sm:mt-0 flex flex-col items-end">
                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${shift.status === 'PENDING_REVIEW' ? 'bg-yellow-100 text-yellow-800' : shift.status === 'APPROVED' ? 'bg-green-100 text-green-800' : shift.status === 'ACTIVE' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                  {shift.status}
                </span>
                {shift.report_data?.screenshot && (
                  <a href={shift.report_data.screenshot} target="_blank" rel="noreferrer" className="text-indigo-600 text-xs hover:underline mt-2 flex items-center">
                    <ImageIcon className="w-3 h-3 mr-1" /> Скриншот
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {showEndModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-xl font-bold text-foreground mb-4">Отчет за смену</h3>
            <form onSubmit={handleEnd} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Скриншот (ссылка)</label>
                <input type="url" required value={reportUrl} onChange={e => setReportUrl(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" placeholder="https://imgur.com/..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Заработанный баланс ($)</label>
                <input type="number" required min="0" step="0.01" value={balance} onChange={e => setBalance(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" placeholder="100.50" />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Заметки (необязательно)</label>
                <textarea value={notes} onChange={e => setNotes(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" rows={3} placeholder="Любые комментарии..." />
              </div>
              <div className="flex justify-end space-x-3 pt-4 border-t border-border mt-6">
                <button type="button" onClick={() => setShowEndModal(false)} className="px-4 py-2 text-muted-foreground hover:bg-muted rounded-lg transition-colors">Отмена</button>
                <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors">Отправить</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
