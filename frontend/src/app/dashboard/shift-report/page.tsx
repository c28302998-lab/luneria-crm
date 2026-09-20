'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { DollarSign, Upload, CheckCircle2 } from 'lucide-react';

export default function ShiftReportPage() {
  const { user } = useAuth();
  const [amount, setAmount] = useState('');
  const [notes, setNotes] = useState('');
  const [links, setLinks] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!amount) return;
    try {
      await api.post('/shift-reports/', {
        amount: parseFloat(amount),
        files: links ? [links] : [],
        notes: notes
      });
      setSuccess(true);
      setAmount('');
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      alert("Ошибка при отправке отчета");
    }
  };

  if (user?.role !== 'WORKER') return <div className="p-6">Доступно только работникам</div>;

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-foreground">Сдать смену</h2>
      
      <div className="bg-card rounded-2xl shadow-sm border border-border p-6">
        {success ? (
          <div className="text-center py-10">
            <div className="w-16 h-16 bg-green-100 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2">Отчет принят!</h3>
            <p className="text-muted-foreground">Сумма будет зачислена на баланс после проверки.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">Заработок за смену ($)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <DollarSign className="h-5 w-5 text-muted-foreground" />
                </div>
                <input 
                  type="number" step="0.01" required 
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="pl-10 block w-full rounded-xl border border-border bg-background p-3 text-foreground focus:ring-2 focus:ring-primary focus:outline-none" 
                  placeholder="0.00"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">Ник рабочего аккаунта / Ваше имя</label>
              <input 
                type="text" required 
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="block w-full rounded-xl border border-border bg-background p-3 text-foreground focus:ring-2 focus:ring-primary focus:outline-none" 
                placeholder="Например: Qwerty/Алексей"
              />
            </div>
            
            <div className="bg-pink-50 text-pink-800 p-4 rounded-xl text-sm border border-pink-100">
              <strong className="block mb-1">Важно:</strong>
              Продажи считаются ВСЕ, которые вы сделали за день (неважно, ваши 20% или нет). 
              Скидывайте сюда всё, что продали за сегодня.
            </div>

            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">Скриншоты статистики (Ссылка на Imgur/Postimages)</label>
              <input 
                type="url" required 
                value={links}
                onChange={(e) => setLinks(e.target.value)}
                className="block w-full rounded-xl border border-border bg-background p-3 text-foreground focus:ring-2 focus:ring-primary focus:outline-none" 
                placeholder="https://imgur.com/..."
              />
            </div>
            
            <button type="submit" className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-bold shadow-lg shadow-primary/20 hover:scale-[1.02] transition-transform">
              Отправить отчет
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
