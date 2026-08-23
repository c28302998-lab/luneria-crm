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
  const [usersMap, setUsersMap] = useState<Record<number, string>>({});
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

      const uMap: Record<number, string> = {};
      usersRes.data.forEach((u: any) => {
        uMap[u.id] = u.name;
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
    return c.first_name.toLowerCase().includes(search.toLowerCase()) || 
           c.telegram.toLowerCase().includes(search.toLowerCase());
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">Работники</h2>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex space-x-4">
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
          <div className="p-8 text-center text-gray-500">Загрузка...</div>
        ) : filteredWorkers.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>Работники не найдены</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Работник</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Контакты</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Админ</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Партнер</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Переведен</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredWorkers.map(w => {
                  const candidate = candidatesMap[w.candidate_id];
                  const adminName = usersMap[w.admin_id];
                  return (
                    <tr key={w.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {candidate ? candidate.first_name : `ID Кандидата #${w.candidate_id}`}
                        </div>
                        <div className="text-xs text-gray-500">Worker ID #{w.id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {candidate ? (
                          <>
                            <div>{candidate.telegram}</div>
                            <div className="text-xs">{candidate.email}</div>
                          </>
                        ) : 'Нет данных'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          {w.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {adminName || `ID #${w.admin_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {w.partner_id ? `Партнер #${w.partner_id}` : 'Не назначен'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(w.created_at).toLocaleDateString('ru-RU')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex justify-end space-x-4">
                        <Link href={`/dashboard/workers/${w.id}`} className="text-indigo-600 hover:text-indigo-900">
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
