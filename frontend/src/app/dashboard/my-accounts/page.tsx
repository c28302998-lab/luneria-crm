'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { MonitorSmartphone } from 'lucide-react';

export default function MyAccountsPage() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const { data } = await api.get('/telegram/proxy/my-accounts');
        setAccounts(data);
      } catch (e) {}
    };
    if (user) fetchAccounts();
  }, [user]);

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
        <MonitorSmartphone className="w-6 h-6 text-pink-500" /> Мои Telegram Аккаунты
      </h2>
      <div className="bg-white shadow-sm rounded-xl border border-slate-200 p-6">
        {accounts.length === 0 ? (
          <p className="text-slate-500">У вас пока нет привязанных аккаунтов.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {accounts.map(acc => (
              <div key={acc.id} className="p-5 border border-pink-200 rounded-xl bg-pink-50">
                <p className="font-bold text-slate-800 text-lg mb-4">{acc.name || `Аккаунт #${acc.id}`}</p>
                <div className="space-y-3">
                  <div>
                    <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Номер</span>
                    <p className="font-medium text-slate-900">{acc.phone || '—'}</p>
                  </div>
                  {acc.username && (
                    <div>
                      <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Username</span>
                      <p className="font-medium text-slate-900">@{acc.username.replace('@', '')}</p>
                    </div>
                  )}
                </div>
                <div className="mt-4 pt-4 border-t border-pink-200/50">
                  <span className="text-xs text-green-700 bg-green-200/50 px-2 py-1 rounded-full font-bold">
                    Выдан вам
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
