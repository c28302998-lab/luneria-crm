'use client';

import { useAuth } from '@/store/auth';
import { DollarSign, Calendar } from 'lucide-react';
import { api } from '@/lib/api';
import { useState, useEffect } from 'react';

export default function MyBalancePage() {
  const { user } = useAuth();
  const [balance, setBalance] = useState(0);
  const [payoutDate, setPayoutDate] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const { data } = await api.get(`/users/${user?.id}`);
        setBalance(data.balance || 0);
        setPayoutDate(data.payout_date);
      } catch (error) {
        console.error("Failed to fetch balance", error);
      } finally {
        setLoading(false);
      }
    };
    if (user?.id) fetchUserData();
  }, [user]);

  if (loading) {
    return <div className="p-6 text-foreground">Загрузка...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-foreground mb-6">Мой баланс</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-indigo-900 to-slate-900 rounded-2xl shadow-lg p-8 text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500 opacity-20 rounded-full blur-3xl -mr-10 -mt-10"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-emerald-500 opacity-10 rounded-full blur-3xl -ml-10 -mb-10"></div>
          
          <div className="relative z-10">
            <div className="flex items-center mb-6 text-indigo-300">
              <DollarSign className="w-6 h-6 mr-2" />
              <h3 className="text-lg font-bold">Заработано за месяц</h3>
            </div>
            <div className="text-5xl font-extrabold tracking-tight mb-2">
              ${balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-indigo-200 text-sm mt-4">
              Это ваш текущий баланс, подтвержденный руководством.
            </p>
          </div>
        </div>

        <div className="bg-card rounded-2xl shadow-sm border border-border p-8 flex flex-col justify-center">
          <div className="flex items-center mb-6 text-muted-foreground">
            <Calendar className="w-6 h-6 mr-3 text-primary" />
            <h3 className="text-lg font-bold text-foreground">Дата ближайшей выплаты</h3>
          </div>
          {payoutDate ? (
            <div className="text-4xl font-bold text-foreground">
              {new Date(payoutDate).toLocaleDateString('ru-RU', { 
                day: 'numeric', 
                month: 'long', 
                year: 'numeric' 
              })}
            </div>
          ) : (
            <div className="text-2xl font-medium text-muted-foreground">
              Дата еще не назначена
            </div>
          )}
          <p className="text-muted-foreground text-sm mt-6">
            Средства будут переведены по вашим реквизитам в указанную дату.
          </p>
        </div>
      </div>
    </div>
  );
}
