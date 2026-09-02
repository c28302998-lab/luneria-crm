'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Key } from 'lucide-react';

type TabType = 'ALL' | 'FREE' | 'EMAILS';

export default function AccountsPage() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [workers, setWorkers] = useState<any[]>([]);
  const [partners, setPartners] = useState<any[]>([]);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [emails, setEmails] = useState<any[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState<any>(null);
  
  const [activeTab, setActiveTab] = useState<TabType>('ALL');

  const handleSyncLegacy = async () => {
    if (!confirm('Синхронизировать старые TG аккаунты в эту таблицу?')) return;
    try {
      const res = await api.post('/telegram/admin/accounts/sync-legacy');
      alert(`Синхронизировано аккаунтов: ${res.data.synced}`);
      window.location.reload();
    } catch (err) {
      alert('Ошибка синхронизации');
    }
  };


  const [formData, setFormData] = useState({
    login: '',
    account_number: '',
    worker_id: '',
    partner_id: '',
    status: 'FREE'
  });

  const [emailForm, setEmailForm] = useState({
    email: '',
    linked_account_name: ''
  });

  const fetchData = async () => {
    try {
      const p = [
        api.get('/accounts/'),
        api.get('/workers/'),
        api.get('/partners/'),
        api.get('/candidates/')
      ];
      if (user?.role === 'OWNER' || user?.role === 'CURATOR') {
        p.push(api.get('/accounts/emails'));
      }
      const res = await Promise.all(p);
      setAccounts(res[0].data);
      setWorkers(res[1].data);
      setPartners(res[2].data);
      setCandidates(res[3].data);
      if (res[4]) {
        setEmails(res[4].data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user]);

  
  const handleEditAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        login: editingAccount.login,
        status: editingAccount.status,
      };
      if (editingAccount.account_number) payload.account_number = editingAccount.account_number;
      if (editingAccount.worker_id) payload.worker_id = parseInt(editingAccount.worker_id);
      if (editingAccount.partner_id) payload.partner_id = parseInt(editingAccount.partner_id);
      
      await api.patch(`/accounts/${editingAccount.id}`, payload);
      setEditingAccount(null);
      fetchData();
    } catch (err: any) {
      alert('Ошибка при сохранении: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        login: formData.login,
        status: activeTab === 'FREE' ? 'FREE' : formData.status,
      };
      if (formData.account_number) payload.account_number = formData.account_number;
      if (activeTab !== 'FREE') {
        if (formData.worker_id) payload.worker_id = parseInt(formData.worker_id);
        if (formData.partner_id) payload.partner_id = parseInt(formData.partner_id);
      }
      
      await api.post('/accounts/', payload);
      setShowModal(false);
      setFormData({ login: '', account_number: '', worker_id: '', partner_id: '', status: 'FREE' });
      fetchData();
    } catch (err: any) {
      console.error(err);
      alert('Ошибка при создании: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleUpdateStatus = async (id: number, newStatus: string) => {
    try {
      await api.patch(`/accounts/${id}`, { status: newStatus });
      fetchData();
    } catch (err) {
      alert('Ошибка при обновлении статуса');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить аккаунт?')) return;
    try {
      await api.delete(`/accounts/${id}`);
      fetchData();
    } catch (err) {
      alert('Ошибка при удалении');
    }
  };

  const handleCreateEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = { email: emailForm.email };
      if (emailForm.linked_account_name) payload.linked_account_name = emailForm.linked_account_name;
      await api.post('/accounts/emails', payload);
      setShowEmailModal(false);
      setEmailForm({ email: '', linked_account_name: '' });
      fetchData();
    } catch (err: any) {
      console.error(err);
      alert('Ошибка при создании почты: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeleteEmail = async (id: number) => {
    if (!confirm('Удалить почту?')) return;
    try {
      await api.delete(`/accounts/emails/${id}`);
      fetchData();
    } catch (err) {
      alert('Ошибка при удалении');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'FREE': return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">Свободен</span>;
      case 'ISSUED': return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">Выдан</span>;
      case 'IN_PROGRESS': return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">В работе</span>;
      case 'ISSUE': return <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">Проблема</span>;
      case 'NEEDS_REPLACEMENT': return <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-medium">На замену</span>;
      case 'RETURNED': return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">Возвращен</span>;
      case 'RECEIVED': return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">Получен</span>;
      default: return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">{status}</span>;
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Загрузка...</div>;

  const displayAccounts = activeTab === 'FREE' ? accounts.filter(a => a.status === 'FREE') : accounts;

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Key className="w-6 h-6 mr-3 text-indigo-600" />
          Инвентарь аккаунтов
        </h1>
        {(user?.role === 'OWNER' || user?.role === 'CURATOR') && activeTab !== 'EMAILS' && (
          <button 
            onClick={() => setShowModal(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
          >
            + Добавить аккаунт
          </button>
        )}
        {(user?.role === 'OWNER' || user?.role === 'CURATOR') && activeTab === 'EMAILS' && (
          <button 
            onClick={() => setShowEmailModal(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
          >
            + Добавить почту
          </button>
        )}
      </div>

      {(user?.role === 'OWNER' || user?.role === 'CURATOR') && (
        <div className="flex space-x-6 border-b border-gray-200">
          <button 
            onClick={() => setActiveTab('ALL')} 
            className={`pb-2 text-sm font-medium transition-colors ${activeTab === 'ALL' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Все аккаунты
          </button>
          <button 
            onClick={() => setActiveTab('FREE')} 
            className={`pb-2 text-sm font-medium transition-colors ${activeTab === 'FREE' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Свободные / Новые
          </button>
          <button 
            onClick={() => setActiveTab('EMAILS')} 
            className={`pb-2 text-sm font-medium transition-colors ${activeTab === 'EMAILS' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Почты к аккаунтам
          </button>
        </div>
      )}

      {activeTab !== 'EMAILS' ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-50/50 border-b border-gray-100">
                <tr>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID / Логин / Номер</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">За кем закреплен</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Партнер</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Дата выдачи</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Статус</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Действия</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {displayAccounts.map(acc => {
                  const worker = workers.find(w => w.id === acc.worker_id);
                  const partner = partners.find(p => p.id === acc.partner_id);
                  const workerCandidate = worker ? candidates.find(c => c.id === worker.candidate_id) : null;
                  const workerName = workerCandidate ? `${workerCandidate.first_name} ${workerCandidate.last_name}`.trim() : 'Worker';
                  
                  return (
                    <tr key={acc.id} className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="font-medium text-gray-900">#{acc.id} {acc.login}</div>
                        {acc.account_number && <div className="text-gray-500 text-xs">Номер: {acc.account_number}</div>}
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
                              <>
                                <button onClick={() => setEditingAccount(acc)} className="text-blue-600 hover:text-blue-900 ml-3">
                                  Редактировать
                                </button>
                                <button onClick={() => handleDelete(acc.id)} className="text-red-600 hover:text-red-900 ml-3">
                                  Удалить
                                </button>
                              </>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {displayAccounts.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-500">Нет аккаунтов</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50/50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Адрес почты</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Привязана к аккаунту</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {emails.map(email => {
                const linkedAcc = accounts.find(a => a.id === email.account_id);
                return (
                  <tr key={email.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{email.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{email.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {email.linked_account_name || 'Не привязана'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button onClick={() => handleDeleteEmail(email.id)} className="text-red-600 hover:text-red-900">
                        Удалить
                      </button>
                    </td>
                  </tr>
                );
              })}
              {emails.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">Нет сохраненных почт</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Добавить аккаунт {activeTab === 'FREE' && '(Свободный)'}</h3>
            <form onSubmit={handleCreateAccount} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Имя аккаунта (Логин / Ник) *</label>
                <input
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.login}
                  onChange={(e) => setFormData({...formData, login: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Номер аккаунта (Опционально)</label>
                <input
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={formData.account_number}
                  onChange={(e) => setFormData({...formData, account_number: e.target.value})}
                />
              </div>

              {activeTab === 'ALL' && (
                <>
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
                </>
              )}

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

      {showEmailModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Добавить почту</h3>
            <form onSubmit={handleCreateEmail} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Адрес почты *</label>
                <input
                  required
                  type="email"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={emailForm.email}
                  onChange={(e) => setEmailForm({...emailForm, email: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Привязана за аккаунтом (Напишите имя аккаунта)</label>
                <input
                  type="text"
                  placeholder="Например: user123"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={emailForm.linked_account_name}
                  onChange={(e) => setEmailForm({...emailForm, linked_account_name: e.target.value})}
                />
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowEmailModal(false)}
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

      {/* Edit Account Modal */}
      {editingAccount && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Редактировать аккаунт</h3>
            <form onSubmit={handleEditAccount} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Имя аккаунта (Логин / Ник) *</label>
                <input
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={editingAccount.login || ''}
                  onChange={(e) => setEditingAccount({...editingAccount, login: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Номер аккаунта (Опционально)</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={editingAccount.account_number || ''}
                  onChange={(e) => setEditingAccount({...editingAccount, account_number: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Работник (Опционально)</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={editingAccount.worker_id || ''}
                  onChange={(e) => setEditingAccount({...editingAccount, worker_id: e.target.value})}
                >
                  <option value="">-- Не выбран --</option>
                  {workers.map(w => {
                    const c = candidates.find(c => c.id === w.candidate_id);
                    return (
                      <option key={w.id} value={w.id}>[{w.id}] {c?.name || 'Worker'}</option>
                    );
                  })}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Партнер (Опционально)</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={editingAccount.partner_id || ''}
                  onChange={(e) => setEditingAccount({...editingAccount, partner_id: e.target.value})}
                >
                  <option value="">-- Не выбран --</option>
                  {partners.map(p => (
                    <option key={p.id} value={p.id}>[{p.id}] {p.name}</option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setEditingAccount(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
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
