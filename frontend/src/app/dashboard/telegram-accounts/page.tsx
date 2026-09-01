'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { MonitorSmartphone, Plus, Link as LinkIcon, Unlink, Lock, Activity, Loader2, Eye, EyeOff, Trash, CheckSquare } from 'lucide-react';

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
  const [authStep, setAuthStep] = useState(1);
  const [showChecklistModal, setShowChecklistModal] = useState<number | null>(null);
  const [checklistText, setChecklistText] = useState('');
  const [savingChecklist, setSavingChecklist] = useState(false); // 1: phone, 2: code, 3: password
  const [loading, setLoading] = useState(false);


  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите полностью удалить этот аккаунт из CRM?')) return;
    try {
      await api.delete(`/telegram/admin/accounts/${id}`);
      fetchAccounts();
    } catch (err) {
      alert('Ошибка при удалении аккаунта');
    }
  };

  const fetchAccounts = async () => {

    try {
      const { data } = await api.get('/telegram/admin/accounts');
      setAccounts(data);
    } catch (err: any) {}
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

    const [showStatsModal, setShowStatsModal] = useState<number | null>(null);
  const [statsData, setStatsData] = useState<any>(null);
  
  const handleOpenStats = async (accId: number) => {
    setShowStatsModal(accId);
    setStatsData(null);
    try {
      const { data } = await api.get(`/telegram/admin/accounts/${accId}/stats`);
      setStatsData(data);
    } catch (err: any) {
      console.error("Error fetching stats", err);
    }
  };
  
  const handleUpdateStatus = async (accId: number, status: string) => {
    if (!confirm(`Изменить статус аккаунта на ${status}?`)) return;
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/status`, { status });
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка изменения статуса');
    }
  };

  
  const handleToggleMask = async (accId: number, current: boolean) => {
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/mask`, { mask_client_names: !current });
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка изменения настройки');
    }
  };

  const handleAssign = async (accId: number, userId: string) => {
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/assign`, {
        user_id: userId ? parseInt(userId) : null
      });
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Ошибка при назначении');
    }
  };

  const handleRevoke = async (accId: number) => {
    if (!confirm('Вы уверены, что хотите отозвать доступ и заморозить аккаунт?')) return;
    try {
      await api.post(`/telegram/admin/accounts/${accId}/revoke`);
      fetchAccounts();
    } catch (err: any) {
      alert('Ошибка при отзыве');
    }
  };

  return (
    <div>

      {/* Stats Modal */}
      {showStatsModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-[60]">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Мониторинг аккаунта #{showStatsModal}</h3>
              <button onClick={() => setShowStatsModal(null)} className="text-gray-400 hover:text-gray-500">×</button>
            </div>
            
            {!statsData ? (
              <div className="flex justify-center p-8"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-500">Статус</span>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${statsData.is_online ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                    <span className="text-sm font-bold">{statsData.is_online ? 'Онлайн' : 'Оффлайн'}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="text-xs text-gray-500 mb-1">Всего сообщений</div>
                    <div className="text-lg font-semibold">{statsData.total_messages}</div>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="text-xs text-gray-500 mb-1">Время работы</div>
                    <div className="text-lg font-semibold">{Math.round(statsData.total_work_seconds / 60)} мин</div>
                  </div>
                </div>
                
                <div className="border-t border-gray-100 pt-4 space-y-2">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Технические данные</h4>
                  
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Последняя активность:</span>
                    <span className="text-gray-900">{statsData.last_activity ? new Date(statsData.last_activity).toLocaleString('ru-RU') : 'Нет данных'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Последний IP:</span>
                    <span className="text-gray-900">{statsData.last_ip || 'Неизвестно'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Устройство:</span>
                    <span className="text-gray-900 truncate max-w-[150px]" title={`${statsData.last_os} / ${statsData.last_browser}`}>{statsData.last_os || 'Неизвестно'}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

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
                                    <select 
                    value={acc.status}
                    onChange={(e) => handleUpdateStatus(acc.id, e.target.value)}
                    className={`px-2 py-1 text-xs font-semibold rounded-full border-none cursor-pointer outline-none ${
                      acc.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 
                      acc.status === 'FROZEN' ? 'bg-blue-100 text-blue-800' : 
                      acc.status === 'BLOCKED' ? 'bg-red-100 text-red-800' : 
                      'bg-gray-100 text-gray-800'
                    }`}
                  >
                                        <option value="ACTIVE">Активен</option>
                    <option value="REVOKED">Отозван</option>
                    <option value="FROZEN">Заморожен</option>
                    <option value="BLOCKED">Заблокирован</option>
                    <option value="DISABLED">Отключен</option>
                  </select>
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
                                                                        <div className="flex flex-col gap-2">
                    <button onClick={() => handleRevoke(acc.id)} className="text-red-600 hover:text-red-900 flex items-center gap-1 text-xs">
                      <Unlink className="w-4 h-4" /> Отозвать (откл. сессию)
                    </button>
                    {user?.role === 'OWNER' && (
                      <button onClick={() => handleDelete(acc.id)} className="text-red-700 font-bold hover:text-red-900 flex items-center gap-1 text-xs">
                        <Trash className="w-4 h-4" /> Удалить из CRM
                      </button>
                    )}
                    {user?.role === 'OWNER' && (
                      <button onClick={() => { setShowChecklistModal(acc.id); setChecklistText(acc.setup_checklist || ''); }} className="text-blue-600 hover:text-blue-900 flex items-center gap-1 text-xs">
                        <CheckSquare className="w-4 h-4" /> Задачи админу
                      </button>
                    )}
                    <button onClick={() => handleOpenStats(acc.id)} className="text-indigo-600 hover:text-indigo-900 flex items-center gap-1 text-xs">
                      <Activity className="w-4 h-4" /> Статистика
                    </button>
                    <button onClick={() => handleToggleMask(acc.id, !!acc.mask_client_names)} className="text-gray-600 hover:text-gray-900 flex items-center gap-1 text-xs">
                      {acc.mask_client_names ? <EyeOff className="w-4 h-4 text-orange-500" /> : <Eye className="w-4 h-4" />}
                      Анонимность: {acc.mask_client_names ? 'ВКЛ' : 'ВЫКЛ'}
                    </button>
                  </div>
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


      {/* Checklist Edit Modal */}
      {showChecklistModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Персональные задачи для Админа</h3>
              <button onClick={() => setShowChecklistModal(null)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="p-6">
              <p className="text-sm text-gray-500 mb-4">Напишите список задач (по одной на каждой строке), которые админ должен выполнить при работе с этим аккаунтом перед выдачей кандидату.</p>
              <textarea
                value={checklistText}
                onChange={e => setChecklistText(e.target.value)}
                className="w-full h-48 border border-gray-300 rounded-lg p-3 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Например:
Сменить пароль
Отписать куратору"
              />
            </div>
            <div className="p-4 bg-gray-50 flex justify-end gap-3 border-t border-gray-100">
              <button onClick={() => setShowChecklistModal(null)} className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50">Отмена</button>
              <button 
                onClick={async () => {
                  setSavingChecklist(true);
                  try {
                    await api.patch(`/telegram/admin/accounts/${showChecklistModal}/checklist`, { setup_checklist: checklistText });
                    fetchAccounts();
                    setShowChecklistModal(null);
                  } catch (err) {
                    alert('Ошибка сохранения');
                  } finally {
                    setSavingChecklist(false);
                  }
                }}
                disabled={savingChecklist}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
              >
                {savingChecklist ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          </div>
        </div>
      )}

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
