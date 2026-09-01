'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { MonitorSmartphone, Plus, Link as LinkIcon, Unlink, Lock } from 'lucide-react';

export default function TelegramAccountsPage() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [candidates, setCandidates] = useState<any[]>([]);
  
  const [showAddModal, setShowAddModal] = useState(false);
  
  // Auth states
  const [phone, setPhone] = useState('');
  const [accountName, setAccountName] = useState('');
  const [phoneCodeHash, setPhoneCodeHash] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [authStep, setAuthStep] = useState(1); // 1: phone, 2: code, 3: password
  const [loading, setLoading] = useState(false);

  const fetchAccounts = async () => {
    try {
      const { data } = await api.get('/telegram/admin/accounts');
      setAccounts(data);
    } catch (err) {}
  };

  useEffect(() => {
    if (user?.role === 'OWNER') {
      fetchAccounts();
      api.get('/users/').then(res => setUsers(res.data)).catch(console.error);
      api.get('/candidates/').then(res => setCandidates(res.data)).catch(console.error);
    }
  }, [user]);

  if (user?.role !== 'OWNER') return <div>Access Denied</div>;

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/telegram/admin/auth/send-code', { phone });
      setPhoneCodeHash(data.phone_code_hash);
      setAuthStep(2);
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/telegram/admin/auth/verify-code', { 
        phone, code, password: password || null, account_name: accountName
      });
      if (data.status === '2FA_REQUIRED') {
        setAuthStep(3);
      } else {
        setShowAddModal(false);
        setAuthStep(1);
        setPhone(''); setCode(''); setPassword(''); setAccountName('');
        fetchAccounts();
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async (accId: number, userId: string) => {
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/assign`, {
        user_id: userId ? parseInt(userId) : null
      });
      fetchAccounts();
    } catch (err) {
      alert('Ошибка при назначении');
    }
  };

  const handleRevoke = async (accId: number) => {
    if (!confirm('Вы уверены, что хотите отозвать доступ и заморозить аккаунт?')) return;
    try {
      await api.post(`/telegram/admin/accounts/${accId}/revoke`);
      fetchAccounts();
    } catch (err) {
      alert('Ошибка при отзыве');
    }
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
          <MonitorSmartphone className="w-6 h-6 text-indigo-600" />
          Telegram Аккаунты компании
        </h1>
        <button
          onClick={() => { setAuthStep(1); setShowAddModal(true); }}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          <Plus className="w-4 h-4" />
          Добавить аккаунт
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID / Имя</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Телефон</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Назначен</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Активность</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {accounts.map(acc => (
              <tr key={acc.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">#{acc.id} {acc.name}</div>
                  <div className="text-sm text-gray-500">{acc.username || 'Нет username'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{acc.phone}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    acc.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {acc.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <select
                    className="border border-gray-300 rounded-md text-sm p-1"
                    value={acc.assigned_user_id || ''}
                    onChange={(e) => handleAssign(acc.id, e.target.value)}
                  >
                    <option value="">Не назначен</option>
                    {users.filter(u => u.role !== 'CANDIDATE').map(u => (
                      <option key={u.id} value={u.id}>{u.name} (Роль: {u.role})</option>
                    ))}
                  </select>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div>Отправлено: {acc.total_messages_sent}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button onClick={() => handleRevoke(acc.id)} className="text-red-600 hover:text-red-900 flex items-center gap-1">
                    <Unlink className="w-4 h-4" /> Отозвать
                  </button>
                </td>
              </tr>
            ))}
            {accounts.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                  Нет подключенных Telegram аккаунтов. Нажмите "Добавить аккаунт", чтобы авторизовать первый.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Подключение Telegram аккаунта</h3>
            
            {authStep === 1 && (
              <form onSubmit={handleSendCode} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Имя профиля (внутри CRM)</label>
                  <input type="text" required className="w-full px-3 py-2 border rounded-lg" value={accountName} onChange={e => setAccountName(e.target.value)} placeholder="Например: Support 1" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Номер телефона</label>
                  <input type="text" required className="w-full px-3 py-2 border rounded-lg" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+79991234567" />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">Отмена</button>
                  <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
                    {loading ? 'Отправка...' : 'Отправить код'}
                  </button>
                </div>
              </form>
            )}

            {authStep === 2 && (
              <form onSubmit={handleVerifyCode} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Код из Telegram</label>
                  <input type="text" required className="w-full px-3 py-2 border rounded-lg" value={code} onChange={e => setCode(e.target.value)} placeholder="12345" />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setAuthStep(1)} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">Назад</button>
                  <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
                    {loading ? 'Проверка...' : 'Войти'}
                  </button>
                </div>
              </form>
            )}

            {authStep === 3 && (
              <form onSubmit={handleVerifyCode} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Облачный пароль (2FA)</label>
                  <input type="password" required className="w-full px-3 py-2 border rounded-lg" value={password} onChange={e => setPassword(e.target.value)} placeholder="Ваш пароль" />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setAuthStep(2)} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">Назад</button>
                  <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
                    {loading ? 'Проверка...' : 'Войти'}
                  </button>
                </div>
              </form>
            )}

          </div>
        </div>
      )}
    </div>
  );
}
