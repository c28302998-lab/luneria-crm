'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Key, Plus, Check, CheckCircle2, User } from 'lucide-react';


export default function AccountRequestsPage() {
  const { user } = useAuth();
  const [requests, setRequests] = useState<any[]>([]);
  const [partners, setPartners] = useState<any[]>([]);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    candidate_id: '',
    candidate_name: '',
    age: '',
    account_type: '',
    candidate_nickname: '',
    candidate_tg: '',
    questionnaire: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [reqRes, partRes, candRes] = await Promise.all([
        api.get('/account-requests/'),
        api.get('/partners/'),
        api.get('/candidates/')
      ]);
      setRequests(reqRes.data);
      setPartners(partRes.data);
      setCandidates(candRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/account-requests/', {
        ...formData,
        candidate_id: formData.candidate_id ? parseInt(formData.candidate_id) : null,
        admin_nickname: user?.name || 'Админ'
      });
      setShowModal(false);
      fetchData();
    } catch (err) {
      alert('Ошибка при создании заявки');
    }
  };

  const handleUpdateStatus = async (id: number, status: string, partner_id?: number, issued_account_name?: string) => {
    try {
      await api.patch(`/account-requests/${id}/status`, { status, partner_id, issued_account_name });
      fetchData();
    } catch (err) {
      alert((err as any).response?.data?.detail || 'Ошибка при обновлении статуса');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING': return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">Ожидает</span>;
      case 'ACCEPTED': return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">В работе</span>;
      case 'ISSUED': return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">Выдано</span>;
      default: return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">{status}</span>;
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Загрузка...</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
          <Key className="w-6 h-6 text-indigo-600" />
          Заявки на аккаунты
        </h1>
        {(user?.role === 'ADMIN' || user?.role === 'CURATOR') && (
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <Plus className="w-4 h-4" />
            Создать заявку
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Кандидат / ТГ</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Анкета</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Админ</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Тип / Возраст</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {requests.map((req) => (
              <tr key={req.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(req.created_at.endsWith('Z') ? req.created_at : req.created_at + 'Z').toLocaleDateString('ru-RU')}
                </td>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{req.candidate_name} {req.candidate_nickname && `(${req.candidate_nickname})`}</div>
                  <div className="text-sm text-blue-600">{req.candidate_tg}</div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                  {req.questionnaire}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {req.admin_nickname}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="font-medium text-gray-900">{req.account_type}</span> / {req.age} лет
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(req.status)}
                  {req.partner_id && (
                    <div className="text-xs text-gray-500 mt-1">
                      Партнер: {partners.find(p => p.id === req.partner_id)?.company_name || 'Неизвестно'}
                    </div>
                  )}
                  {req.issued_account_name && (
                    <div className="text-xs text-green-700 font-medium mt-1">
                      Аккаунт: {req.issued_account_name}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  {(user?.role === 'OWNER' || user?.role === 'CURATOR') && req.status === 'PENDING' && (
                    <div className="flex items-center justify-end gap-2">
                      <select 
                        className="border border-gray-300 rounded text-xs px-2 py-1 w-[150px] truncate"
                        onChange={(e) => handleUpdateStatus(req.id, 'ACCEPTED', parseInt(e.target.value))}
                        defaultValue=""
                      >
                        <option value="" disabled>Назначить партнера...</option>
                        {partners.map(p => (
                          <option key={p.id} value={p.id}>{p.company_name}</option>
                        ))}
                      </select>
                    </div>
                  )}
                  {(user?.role === 'OWNER' || user?.role === 'CURATOR') && req.status === 'ACCEPTED' && (
                    <button
                      onClick={() => {
                        const accName = prompt('Введите имя выданного аккаунта:');
                        if (accName) handleUpdateStatus(req.id, 'ISSUED', undefined, accName);
                      }}
                      className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 flex items-center ml-auto"
                    >
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      Выдано
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {requests.length === 0 && (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-gray-500">Нет заявок</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] flex flex-col">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Заявка на аккаунт</h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
            </div>
            
            <div className="p-6 overflow-y-auto">
              <form id="reqForm" onSubmit={handleSubmit} className="space-y-4">
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Привязать кандидата (опционально)</label>
                  <select 
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    value={formData.candidate_id}
                    onChange={e => {
                      const candId = e.target.value;
                      const cand = candidates.find(c => c.id.toString() === candId);
                      setFormData({ 
                        ...formData, 
                        candidate_id: candId,
                        candidate_name: cand?.first_name || formData.candidate_name,
                        age: cand?.age?.toString() || formData.age,
                        candidate_tg: cand?.telegram || formData.candidate_tg
                      });
                    }}
                  >
                    <option value="">Не выбран</option>
                    {candidates.map(c => (
                      <option key={c.id} value={c.id}>{c.first_name} ({c.telegram})</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Имя кандидата/Ник <span className="text-red-500">*</span></label>
                    <input required type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                      value={formData.candidate_name} onChange={e => setFormData({...formData, candidate_name: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Возраст <span className="text-red-500">*</span></label>
                    <input required type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                      value={formData.age} onChange={e => setFormData({...formData, age: e.target.value})} />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Акаунт ТГ+OМ <span className="text-red-500">*</span></label>
                    <input required type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Например: TG+OM"
                      value={formData.account_type} onChange={e => setFormData({...formData, account_type: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Ник кандидата (если есть)</label>
                    <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                      value={formData.candidate_nickname} onChange={e => setFormData({...formData, candidate_nickname: e.target.value})} />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ТГ основной кандидата <span className="text-red-500">*</span></label>
                  <input required type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="@username"
                    value={formData.candidate_tg} onChange={e => setFormData({...formData, candidate_tg: e.target.value})} />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Анкета кандидата <span className="text-red-500">*</span></label>
                  <textarea required rows={4} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" 
                    value={formData.questionnaire} onChange={e => setFormData({...formData, questionnaire: e.target.value})} />
                </div>

              </form>
            </div>
            
            <div className="p-6 border-t border-gray-100 bg-gray-50 rounded-b-xl flex justify-end gap-3">
              <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">
                Отмена
              </button>
              <button type="submit" form="reqForm" className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
                Отправить заявку
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
