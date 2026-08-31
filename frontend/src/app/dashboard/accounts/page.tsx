'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Key, Plus, AlertCircle, RefreshCw, CheckCircle2 } from 'lucide-react';

export default function AccountsPage() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [workers, setWorkers] = useState<any[]>([]);
  const [partners, setPartners] = useState<any[]>([]);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    login: '',
    worker_id: '',
    partner_id: '',
    status: 'FREE'
  });

  const fetchData = async () => {
    try {
      const [accRes, wRes, pRes, cRes] = await Promise.all([
        api.get('/accounts/'),
        api.get('/workers/'),
        api.get('/partners/'),
        api.get('/candidates/')
      ]);
      setAccounts(accRes.data);
      setWorkers(wRes.data);
      setPartners(pRes.data);
      setCandidates(cRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/accounts/', {
        login: formData.login,
        worker_id: formData.worker_id ? parseInt(formData.worker_id) : null,
        partner_id: formData.partner_id ? parseInt(formData.partner_id) : null,
        status: formData.status
      });
      setShowModal(false);
      setFormData({ login: '', worker_id: '', partner_id: '', status: 'FREE' });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при создании аккаунта');
    }
  };

  const handleUpdateStatus = async (id: number, status: string) => {
    try {
      await api.patch(`/accounts/${id}`, { status });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при обновлении статуса');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить аккаунт?')) return;
    try {
      await api.delete(`/accounts/${id}`);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при удалении');
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      FREE: 'bg-green-100 text-green-800',
      ISSUED: 'bg-blue-100 text-blue-800',
      IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
      ISSUE: 'bg-red-100 text-red-800',
      NEEDS_REPLACEMENT: 'bg-orange-100 text-orange-800',
      RETURNED: 'bg-gray-100 text-gray-800',
      RECEIVED: 'bg-emerald-100 text-emerald-800'
    };
    const labels: Record<string, string> = {
      FREE: 'Свободен',
      ISSUED: 'Выдан',
      IN_PROGRESS: 'В работе',
      ISSUE: 'Проблема',
      NEEDS_REPLACEMENT: 'На замену',
      RETURNED: 'Возвращен',
      RECEIVED: 'Получен'
    };
    return (
      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${colors[status] || colors.FREE}`}>
        {labels[status] || status}
      </span>
    );
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Загрузка...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto overflow-x-hidden">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center space-x-3">
          <Key className="w-8 h-8 text-indigo-600" />
          <h1 className="text-2xl font-bold text-gray-900">
            {user?.role === 'ADMIN' ? 'Мои Аккаунты' : 'Все Аккаунты'}
          </h1>
        </div>
        {(user?.role === 'OWNER' || user?.role === 'CURATOR') && (
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Добавить аккаунт
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50/50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID / Логин</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">За кем закреплен</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Партнер</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата выдачи</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {accounts.map((acc) => {
              const worker = workers.find(w => w.id === acc.worker_id);
              const partner = partners.find(p => p.id === acc.partner_id);
              const workerCandidate = worker ? candidates.find(c => c.id === worker.candidate_id) : null;
              const workerName = workerCandidate ? `${workerCandidate.first_name} ${workerCandidate.last_name}`.trim() : 'Worker';
              
              return (
                <tr key={acc.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="font-medium text-gray-900">#{acc.id}</div>
                    <div className="text-gray-500">{acc.login}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {worker ? `${workerName} (Админ: ID ${worker.admin_id})` : 'Не закреплен'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {partner ? partner.company_name : 'Не выбран'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {acc.issued_at ? new Date(acc.issued_at).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(acc.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {user?.role === 'ADMIN' ? (
                      <div className="flex items-center justify-end space-x-2">
                        {acc.status !== 'RECEIVED' && (
                          <button onClick={() => handleUpdateStatus(acc.id, 'RECEIVED')} className="text-xs bg-green-50 text-green-600 px-2 py-1 rounded border border-green-200 hover:bg-green-100">Получил</button>
                        )}
                        <button onClick={() => handleUpdateStatus(acc.id, 'ISSUE')} className="text-xs bg-red-50 text-red-600 px-2 py-1 rounded border border-red-200 hover:bg-red-100">Проблема</button>
                        <button onClick={() => handleUpdateStatus(acc.id, 'NEEDS_REPLACEMENT')} className="text-xs bg-orange-50 text-orange-600 px-2 py-1 rounded border border-orange-200 hover:bg-orange-100">Нужна замена</button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-end space-x-2">
                        <select 
                          className="border border-gray-300 rounded text-xs px-2 py-1"
                          value={acc.status}
                          onChange={(e) => handleUpdateStatus(acc.id, e.target.value)}
                        >
                          <option value="FREE">Свободен</option>
                          <option value="ISSUED">Выдан</option>
                          <option value="IN_PROGRESS">В работе</option>
                          <option value="ISSUE">Проблема</option>
                          <option value="NEEDS_REPLACEMENT">На замену</option>
                          <option value="RETURNED">Возвращен</option>
                          <option value="RECEIVED">Получен (Админ)</option>
                        </select>
                        {(user?.role === 'OWNER' || user?.role === 'CURATOR') && (
                          <button onClick={() => handleDelete(acc.id)} className="text-red-600 hover:text-red-900 ml-2">
                            Удалить
                          </button>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
            {accounts.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">Нет аккаунтов</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Добавить аккаунт</h3>
            <form onSubmit={handleCreateAccount} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Логин / Ник *</label>
                <input
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.login}
                  onChange={(e) => setFormData({...formData, login: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Работник (Кому выдан)</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.worker_id}
                  onChange={(e) => setFormData({...formData, worker_id: e.target.value})}
                >
                  <option value="">-- Не назначен --</option>
                  {workers.map(w => {
                    const c = candidates.find(cand => cand.id === w.candidate_id);
                    const name = c ? `${c.first_name} ${c.last_name}`.trim() : 'Worker';
                    return <option key={w.id} value={w.id}>{name} (Админ: ID {w.admin_id})</option>
                  })}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Агентство (Партнер)</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.partner_id}
                  onChange={(e) => setFormData({...formData, partner_id: e.target.value})}
                >
                  <option value="">-- Не привязан --</option>
                  {partners.map(p => (
                    <option key={p.id} value={p.id}>{p.company_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Статус</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                >
                  <option value="FREE">Свободен</option>
                  <option value="ISSUED">Выдан</option>
                  <option value="IN_PROGRESS">В работе</option>
                  <option value="ISSUE">Проблема</option>
                  <option value="NEEDS_REPLACEMENT">На замену</option>
                  <option value="RETURNED">Возвращен</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
                >
                  Сохранить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
