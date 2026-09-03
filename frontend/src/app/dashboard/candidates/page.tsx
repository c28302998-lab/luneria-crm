'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, Search, Filter, Key } from 'lucide-react';
import Link from 'next/link';

interface Candidate {
  id: number;
  first_name: string;
  telegram: string;
  email: string;
  status: string;
  admin_id: number;
  created_at: string;
}

export default function CandidatesPage() {
  const { user } = useAuth();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isMyRequestsOpen, setIsMyRequestsOpen] = useState(false);
  const [myRequests, setMyRequests] = useState<any[]>([]);
  
  const openMyRequests = async () => {
    try {
      const { data } = await api.get('/account-requests/');
      setMyRequests(data);
      setIsMyRequestsOpen(true);
    } catch (err) {
      console.error(err);
    }
  };
  const [isRequestModalOpen, setIsRequestModalOpen] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  
  const [reqFormData, setReqFormData] = useState({
    candidate_name: '',
    age: '',
    account_type: '',
    candidate_nickname: '',
    candidate_tg: '',
    questionnaire: ''
  });

  const openRequestModal = (c?: any) => {
    setSelectedCandidate(c || null);
    setReqFormData({
      candidate_name: c?.first_name || '',
      age: c?.age?.toString() || '',
      account_type: '',
      candidate_nickname: '',
      candidate_tg: c?.telegram || '',
      questionnaire: ''
    });
    setIsRequestModalOpen(true);
  };

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/account-requests/', {
        ...reqFormData,
        candidate_id: selectedCandidate?.id || null,
        admin_nickname: user?.name || 'Админ'
      });
      setIsRequestModalOpen(false);
      alert('Заявка успешно создана! Вы можете отследить ее в разделе "Заявки на аккаунт".');
    } catch (err) {
      alert((err as any).response?.data?.detail || 'Ошибка при создании заявки');
    }
  };

  const [formData, setFormData] = useState({
    first_name: '',
    telegram: '',
    email: '',
    source: ''
  });

  const fetchCandidates = async () => {
    try {
      const { data } = await api.get('/candidates/');
      setCandidates(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/candidates/', formData);
      setIsModalOpen(false);
      setFormData({ first_name: '', telegram: '', email: '', source: '' });
      fetchCandidates();
    } catch (err) {
      console.error(err);
      alert('Ошибка при создании кандидата');
    }
  };

  const handleDelete = async (candidateId: number) => {
    if (!confirm('Вы уверены, что хотите удалить кандидата?')) return;
    try {
      await api.delete(`/candidates/${candidateId}`);
      fetchCandidates();
    } catch (err) {
      console.error(err);
      alert('Ошибка при удалении');
    }
  };

  const filteredCandidates = candidates.filter(c => 
    c.status !== 'WORKER' && (statusFilter === 'ALL' || c.status === statusFilter) && (
      c.first_name?.toLowerCase().includes(search.toLowerCase()) ||
      c.telegram?.toLowerCase().includes(search.toLowerCase())
    )
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">Кандидаты</h2>
        
        <div className="flex gap-3">
          {user?.role === 'ADMIN' && (
            <>
              <button 
                onClick={openMyRequests}
                className="flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition"
              >
                Мои заявки
              </button>
              <button 
                onClick={() => openRequestModal()}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition"
              >
                <Key className="h-4 w-4 mr-2" />
                Новая заявка
              </button>
            </>
          )}
          {(user?.role === 'ADMIN' || user?.role === 'OWNER') && (
            <button 
              onClick={() => setIsModalOpen(true)}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
            >
              <Plus className="h-4 w-4 mr-2" />
              Добавить
            </button>
          )}
        </div>
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
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="ALL">Все статусы</option>
            <option value="NEW">Новый</option>
            <option value="IN_PROGRESS">В работе</option>
            <option value="APPROVED">Одобрен</option>
            <option value="REJECTED">Отказ</option>
          </select>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Загрузка...</div>
        ) : filteredCandidates.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>Кандидаты не найдены</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Имя</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Контакты</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата создания</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCandidates.map(c => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{c.first_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{c.telegram}</div>
                      <div className="text-xs">{c.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        c.status === 'NEW' ? 'bg-purple-100 text-purple-800' :
                        c.status === 'IN_PROGRESS' ? 'bg-yellow-100 text-yellow-800' :
                        c.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                        c.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {c.status === 'NEW' ? 'Новый' :
                         c.status === 'IN_PROGRESS' ? 'В работе' :
                         c.status === 'APPROVED' ? 'Одобрен' :
                         c.status === 'REJECTED' ? 'Отказ' : c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(c.created_at).toLocaleDateString('ru-RU')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex items-center justify-end space-x-4">
                      {(user?.role === 'ADMIN' || user?.role === 'OWNER' || user?.role === 'CURATOR') && (
                        <button
                          onClick={() => openRequestModal(c)}
                          className="text-green-600 hover:text-green-900"
                        >
                          Зарегистрировать аккаунт
                        </button>
                      )}
                      <Link href={`/dashboard/candidates/${c.id}`} className="text-indigo-600 hover:text-indigo-900">
                        Открыть
                      </Link>
                      {user?.role === 'OWNER' && (
                        <button 
                          onClick={() => handleDelete(c.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Удалить
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Новый кандидат</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Имя</label>
                <input 
                  type="text" required 
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Telegram</label>
                <input 
                  type="text" 
                  value={formData.telegram}
                  onChange={(e) => setFormData({...formData, telegram: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input 
                  type="email" 
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Отмена
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-indigo-700"
                >
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* My Requests Modal */}
      {isMyRequestsOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Мои заявки на аккаунты</h3>
              <button onClick={() => setIsMyRequestsOpen(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
            </div>
            
            <div className="p-6 overflow-y-auto">
              {myRequests.length === 0 ? (
                <div className="text-center text-gray-500 py-8">У вас еще нет заявок</div>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Дата</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Кандидат</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Тип</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Статус</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Выданный аккаунт</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {myRequests.map(req => (
                      <tr key={req.id}>
                        <td className="px-4 py-3 text-sm text-gray-500">{new Date(req.created_at).toLocaleDateString('ru-RU')}</td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{req.candidate_name}</td>
                        <td className="px-4 py-3 text-sm text-gray-500">{req.account_type}</td>
                        <td className="px-4 py-3 text-sm">
                                                     {['NEW', 'PENDING'].includes(req.status) ? <span className="text-yellow-600">Новая</span> : 
                           ['IN_PROGRESS', 'ACCEPTED'].includes(req.status) ? <span className="text-blue-600">В работе</span> : 
                           req.status === 'READY' ? <span className="text-emerald-600">Готов к выдаче</span> :
                           req.status === 'ISSUED' ? <span className="text-green-600 font-bold">Выдан</span> :
                           req.status === 'ISSUED_TO_ADMIN' ? <span className="text-indigo-600 font-bold">Выдан админу</span> :
                           req.status === 'ISSUE' ? <span className="text-red-600">Проблема</span> :
                           <span className="text-gray-600">Отменена</span>}
                        </td>
                        <td className="px-4 py-3 text-sm font-medium text-green-700">{req.issued_account_name || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}
      {/* Account Request Modal */}
      {isRequestModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Заявка на аккаунт {selectedCandidate ? `для: ${selectedCandidate.first_name}` : ''}</h3>
              <button onClick={() => setIsRequestModalOpen(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
            </div>
            
            <div className="p-6 overflow-y-auto">
              <form id="reqForm" onSubmit={handleCreateRequest} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Имя кандидата/Ник *</label>
                    <input required type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                      value={reqFormData.candidate_name} onChange={e => setReqFormData({...reqFormData, candidate_name: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Возраст *</label>
                    <input required type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                      value={reqFormData.age} onChange={e => setReqFormData({...reqFormData, age: e.target.value})} />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Акаунт ТГ+OМ *</label>
                    <input required type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Например: TG+OM"
                      value={reqFormData.account_type} onChange={e => setReqFormData({...reqFormData, account_type: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Ник кандидата (если есть)</label>
                    <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                      value={reqFormData.candidate_nickname} onChange={e => setReqFormData({...reqFormData, candidate_nickname: e.target.value})} />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ТГ основной кандидата *</label>
                  <input required type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                    value={reqFormData.candidate_tg} onChange={e => setReqFormData({...reqFormData, candidate_tg: e.target.value})} />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Анкета кандидата *</label>
                  <textarea required rows={4} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                    value={reqFormData.questionnaire} onChange={e => setReqFormData({...reqFormData, questionnaire: e.target.value})} />
                </div>
              </form>
            </div>

            <div className="p-6 border-t border-gray-100 bg-gray-50 rounded-b-xl flex justify-end gap-3">
              <button type="button" onClick={() => setIsRequestModalOpen(false)} className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                Отмена
              </button>
              <button type="submit" form="reqForm" className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700">
                Создать заявку
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
