'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, Search, Filter } from 'lucide-react';
import Link from 'next/link';

interface Worker {
  id: number;
  status: string;
  created_at: string;
  candidate_id: number;
  admin_id: number;
  partner_id: number | null;
}

interface Candidate {
  id: number;
  first_name: string;
  telegram: string;
  email: string;
}

export default function WorkersPage() {
  const { user } = useAuth();
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [candidatesMap, setCandidatesMap] = useState<Record<number, Candidate>>({});
  const [usersMap, setUsersMap] = useState<Record<number, any>>({});
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchData = async () => {
    try {
      const [workersRes, candidatesRes, usersRes] = await Promise.all([
        api.get('/workers/'),
        api.get('/candidates/'),
        api.get('/users/')
      ]);
      
      const cMap: Record<number, Candidate> = {};
      candidatesRes.data.forEach((c: Candidate) => {
        cMap[c.id] = c;
      });
      setCandidatesMap(cMap);

      const uMap: Record<number, any> = {};
      usersRes.data.forEach((u: any) => {
        uMap[u.id] = u;
      });
      setUsersMap(uMap);

      setWorkers(workersRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDelete = async (workerId: number) => {
    if (!confirm('Вы уверены, что хотите удалить работника?')) return;
    try {
      await api.delete(`/workers/${workerId}`);
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при удалении');
    }
  };

  const filteredWorkers = workers.filter(w => {
    const c = candidatesMap[w.candidate_id];
    if (!c) return true;
    const fName = c.first_name || '';
    const tGram = c.telegram || '';
    return fName.toLowerCase().includes(search.toLowerCase()) || 
           tGram.toLowerCase().includes(search.toLowerCase());
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-foreground">Работники</h2>
      </div>

      <div className="bg-card rounded-xl shadow-sm border border-border">
        <div className="p-4 border-b border-border flex space-x-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input 
              type="text" 
              placeholder="Поиск по имени или Telegram..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Загрузка...</div>
        ) : filteredWorkers.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <p>Работники не найдены</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-background">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Работник</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Контакты</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Статус</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Админ</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Баланс</th>
                  {user?.role === 'OWNER' && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Партнер</th>
                  )}
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Переведен</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
                {filteredWorkers.map(w => {
                  const candidate = candidatesMap[w.candidate_id];
                  const adminUser = usersMap[w.admin_id];
                  const adminName = adminUser ? adminUser.name : `ID: ${w.admin_id}`;
                  const workerUser = candidate ? Object.values(usersMap).find(u => u.email === candidate.email) : null;
                  return (
                    <tr key={w.id} className="hover:bg-background">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-foreground">
                          {candidate ? candidate.first_name : `ID Кандидата #${w.candidate_id}`}
                        </div>
                        <div className="text-xs text-muted-foreground">Worker ID #{w.id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                        {candidate ? (
                          <>
                            <div>{candidate.telegram}</div>
                            <div className="text-xs">{candidate.email}</div>
                          </>
                        ) : 'Нет данных'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {w.status === 'ACTIVE' ? (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Активен</span>
                        ) : w.status === 'TERMINATED' ? (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Уволен</span>
                        ) : w.status === 'PAUSED' ? (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Пауза</span>
                        ) : (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-muted text-foreground">{w.status}</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                        {adminName}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-primary">
                        {workerUser ? `$${(workerUser.balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '$0.00'}
                      </td>
                      {user?.role === 'OWNER' && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                        {w.partner_id ? `Партнер #${w.partner_id}` : 'Не назначен'}
                      </td>
                      )}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                        {new Date(w.created_at).toLocaleDateString('ru-RU')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex justify-end space-x-4">
                        <Link href={`/dashboard/workers/${w.id}`} className="text-primary hover:text-indigo-900">
                          Профиль
                        </Link>
                        {user?.role === 'OWNER' && (
                          <button 
                            onClick={() => handleDelete(w.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Удалить
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
