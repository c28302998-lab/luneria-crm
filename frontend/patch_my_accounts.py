with open("src/app/dashboard/my-accounts/page.tsx", "r") as f:
    content = f.read()

import re

new_content = """'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Key } from 'lucide-react';

export default function MyAccountsPage() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const { data } = await api.get('/accounts/');
        // Worker only sees accounts assigned to them
        setAccounts(data.filter((a: any) => a.worker_id === user?.id));
      } catch (e) {}
    };
    if (user) fetchAccounts();
  }, [user]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
        <Key className="w-6 h-6 text-pink-500" /> Мои Аккаунты
      </h2>
      <div className="bg-card shadow-sm rounded-xl border border-border p-6">
        {accounts.length === 0 ? (
          <p className="text-muted-foreground">У вас пока нет привязанных аккаунтов.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {accounts.map(acc => (
              <div key={acc.id} className="p-5 border border-pink-200 rounded-xl bg-pink-50">
                <p className="font-semibold text-slate-800 text-lg mb-4">{acc.login}</p>
                <div className="space-y-2">
                  <div>
                    <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Email / Логин</span>
                    <p className="font-medium text-slate-900">{acc.login}</p>
                  </div>
                  <div>
                    <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Пароль</span>
                    <div className="bg-white px-3 py-2 border border-slate-200 rounded font-mono text-sm mt-1">
                      {acc.gmail_password || '—'}
                    </div>
                  </div>
                  {acc.account_number && (
                    <div>
                      <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Номер (если есть)</span>
                      <p className="font-medium text-slate-900">{acc.account_number}</p>
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
"""

with open("src/app/dashboard/my-accounts/page.tsx", "w") as f:
    f.write(new_content)
