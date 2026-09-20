'use client';
import { parsePhoneNumberFromString } from 'libphonenumber-js';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { MonitorSmartphone, Plus, Link as LinkIcon, Unlink, Lock, Activity, Loader2, Eye, EyeOff, Trash, CheckSquare, Key, RefreshCw } from 'lucide-react';


const formatPhone = (phone: string | null) => {
  if (!phone) return '-';
  let p = phone.trim();
  if (!p.startsWith('+')) {
    p = '+' + p;
  }
  const parsed = parsePhoneNumberFromString(p);
  if (parsed) {
    return parsed.formatInternational();
  }
  return phone;
};

export default function TelegramAccountsPage() {

  const { user } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [editingPwdId, setEditingPwdId] = useState<number | null>(null);
  const [editPwdValue, setEditPwdValue] = useState('');
  
  
  const handleOpenHistory = async (id: number) => {
    setShowHistoryModal(id);
    try {
      const res = await api.get(`/telegram/admin/accounts/${id}/history`);
      setAccountHistory(res.data);
    } catch (e) {
      console.error(e);
      alert('Ошибка при загрузке истории');
    }
  };

  const handleSavePwd = async (id: number) => {
    try {
      await api.put(`/telegram/admin/accounts/${id}/2fa-password`, { password: editPwdValue || null });
      setEditingPwdId(null);
      fetchAccounts();
    } catch (err) {
      alert('Ошибка при сохранении пароля');
    }
  };

  
  const [users, setUsers] = useState<any[]>([]);
  
  // History Modal State
  const [showHistoryModal, setShowHistoryModal] = useState<number | null>(null);
  const [accountHistory, setAccountHistory] = useState<any[]>([]);

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
      const { data } = await api.get(`/telegram/admin/accounts?t=${Date.now()}`);
      setAccounts(data);
    } catch (err: any) {}
  };

  useEffect(() => {
    if (user?.role === 'OWNER' || user?.role === 'ADMIN') {
      fetchAccounts();
      api.get('/users/').then(res => setUsers(res.data)).catch(console.error);
      api.get('/candidates/').then(res => setCandidates(res.data)).catch(console.error);
    }
  }, [user]);

  if (user?.role !== 'OWNER' && user?.role !== 'ADMIN') return <div>Access Denied</div>;

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

  const handleAssignAdmin = async (accId: number, userId: string, workerId: string | null) => {
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/assign`, {
        user_id: userId ? parseInt(userId) : null,
        worker_id: workerId ? parseInt(workerId) : null
      });
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Ошибка при назначении');
    }
  };

  const handleAssignWorker = async (accId: number, adminId: string | null, workerId: string) => {
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/assign`, {
        user_id: adminId ? parseInt(adminId) : null,
        worker_id: workerId ? parseInt(workerId) : null
      });
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Ошибка при назначении');
    }
  };


  const handleSync = async (id: number) => {
    try {
      await api.post(`/telegram/admin/accounts/${id}/sync`);
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при синхронизации');
    }
  };

  const handleApproveIssue = async (id: number) => {
    if (!confirm('Выдать пароль админу?')) return;
    try {
      await api.post(`/telegram/admin/accounts/${id}/approve-issue`);
      fetchAccounts();
    } catch (err) {
      alert('Ошибка при одобрении');
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
          <div className="bg-card rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-foreground">Мониторинг аккаунта #{showStatsModal}</h3>
              <button onClick={() => setShowStatsModal(null)} className="text-gray-400 hover:text-muted-foreground">×</button>
            </div>
            
            {!statsData ? (
              <div className="flex justify-center p-8"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-background rounded-lg">
                  <span className="text-sm font-medium text-muted-foreground">Статус</span>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${statsData.is_online ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                    <span className="text-sm font-bold">{statsData.is_online ? 'Онлайн' : 'Оффлайн'}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-background rounded-lg">
                    <div className="text-xs text-muted-foreground mb-1">Всего сообщений</div>
                    <div className="text-lg font-semibold">{statsData.total_messages}</div>
                  </div>
                  <div className="p-3 bg-background rounded-lg">
                    <div className="text-xs text-muted-foreground mb-1">Время работы</div>
                    <div className="text-lg font-semibold">{Math.round(statsData.total_work_seconds / 60)} мин</div>
                  </div>
                </div>
                
                <div className="border-t border-border pt-4 space-y-2">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Технические данные</h4>
                  
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Последняя активность:</span>
                    <span className="text-foreground">{statsData.last_activity ? new Date(statsData.last_activity).toLocaleString('ru-RU') : 'Нет данных'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Последний IP:</span>
                    <span className="text-foreground">{statsData.last_ip || 'Неизвестно'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Устройство:</span>
                    <span className="text-foreground truncate max-w-[150px]" title={`${statsData.last_os} / ${statsData.last_browser}`}>{statsData.last_os || 'Неизвестно'}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <h1 className="text-2xl font-semibold text-foreground flex items-center gap-2">
          <MonitorSmartphone className="w-6 h-6 text-primary" />
          Telegram Аккаунты компании
        </h1>
        {user?.role === 'OWNER' && (
        <button
          onClick={() => { setAuthStep(1); setShowAddModal(true); }}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition"
        >
          <Plus className="w-4 h-4" />
          Добавить аккаунт
        </button>
        )}
      </div>

      <div className="bg-card rounded-xl shadow-sm border border-border overflow-x-auto">
        <table className="min-w-full divide-y divide-border">
          <thead className="bg-background">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">ID / Имя</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Телефон</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Статус</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Назначен</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Активность</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody className="bg-card divide-y divide-border">
            {accounts.map(acc => (
              <tr key={acc.id} className="hover:bg-background">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-foreground">#{acc.id} {acc.name}</div>
                  <div className="text-sm text-muted-foreground flex items-center gap-2">
                    {acc.username || 'Нет username'}
                    <button onClick={() => handleSync(acc.id)} className="text-muted-foreground hover:text-primary transition" title="Синхронизировать имя">
                      <RefreshCw className="w-3 h-3" />
                    </button>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">{formatPhone(acc.phone)}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                                    <select 
                    value={acc.status}
                    onChange={(e) => handleUpdateStatus(acc.id, e.target.value)}
                    className={`px-2 py-1 text-xs font-semibold rounded-full border-none cursor-pointer outline-none ${
                      acc.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 
                      acc.status === 'FROZEN' ? 'bg-blue-100 text-blue-800' : 
                      acc.status === 'BLOCKED' ? 'bg-red-100 text-red-800' : 
                      'bg-muted text-foreground'
                    }`}
                  >
                                        <option value="ACTIVE">Активен</option>
                    <option value="REVOKED">Отозван</option>
                    <option value="FROZEN">Заморожен</option>
                    <option value="BLOCKED">Заблокирован</option>
                    <option value="DISABLED">Отключен</option>
                  </select>
                </td>
                <td className="px-6 py-4 whitespace-nowrap space-y-2">
                  {(user?.role === 'OWNER' || user?.role === 'FINANCE') && (
                    <div>
                      <div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1">Админ / Владелец:</div>
                      <select 
                        value={acc.assigned_user_id || ''}
                        onChange={(e) => handleAssignAdmin(acc.id, e.target.value, acc.assigned_worker_id?.toString() || null)}
                        className="w-full px-2 py-1 text-sm border border-border rounded-lg bg-background text-foreground"
                      >
                        <option value="">Без админа</option>
                        {users.filter(u => ['ADMIN', 'OWNER', 'FINANCE', 'CURATOR'].includes(u.role)).map(u => (
                          <option key={u.id} value={u.id}>{u.name} ({u.role})</option>
                        ))}
                      </select>
                    </div>
                  )}
                  <div>
                    <div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1">Работник / Кандидат:</div>
                    <select 
                      value={acc.assigned_worker_id || ''}
                      onChange={(e) => handleAssignWorker(acc.id, acc.assigned_user_id?.toString() || null, e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-border rounded-lg bg-background text-foreground"
                    >
                      <option value="">Свободен</option>
                      {users.filter(u => u.role === 'WORKER' || u.role === 'CANDIDATE').map(u => (
                        <option key={u.id} value={u.id}>{u.name} ({u.role === 'CANDIDATE' ? 'Кандидат' : 'Воркер'})</option>
                      ))}
                    </select>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                  <div>Отправлено: {acc.total_messages_sent}</div>
                  <div className="mt-2 text-xs">
                    <span className="font-semibold">2FA Пароль:</span><br/>
                    {editingPwdId === acc.id ? (
                      <div className="flex items-center gap-1 mt-1">
                        <input 
                          type="text" 
                          className="border border-gray-300 rounded px-1 py-0.5 w-24 text-xs" 
                          value={editPwdValue} 
                          onChange={e => setEditPwdValue(e.target.value)} 
                          placeholder="Нет пароля"
                        />
                        <button onClick={() => handleSavePwd(acc.id)} className="text-green-600 font-bold hover:text-green-800">✓</button>
                        <button onClick={() => setEditingPwdId(null)} className="text-red-600 font-bold hover:text-red-800">✕</button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 mt-1">
                        <span className="text-gray-700 font-mono">{acc.two_fa_password || <span className="text-gray-400 italic">Нет пароля</span>}</span>
                        <button onClick={() => { setEditingPwdId(acc.id); setEditPwdValue(acc.two_fa_password || ''); }} className="text-blue-500 hover:text-blue-700 text-[10px] ml-1 flex items-center gap-0.5"><Key className="w-3 h-3"/> ИЗМЕНИТЬ</button>
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                                                                        <div className="flex flex-col gap-2">
                    {acc.issue_request_status === 'REQUESTED' && (
                      <button onClick={() => handleApproveIssue(acc.id)} className="text-orange-600 font-bold hover:text-orange-900 flex items-center gap-1 text-xs">
                        <Key className="w-4 h-4 animate-pulse" /> Одобрить выдачу 2FA
                      </button>
                    )}
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
                    <button onClick={() => handleOpenStats(acc.id)} className="text-primary hover:text-indigo-900 flex items-center gap-1 text-xs">
                      <Activity className="w-4 h-4" /> Статистика
                    </button>
                    <button onClick={() => handleToggleMask(acc.id, !!acc.mask_client_names)} className="text-muted-foreground hover:text-foreground flex items-center gap-1 text-xs">
                      {acc.mask_client_names ? <EyeOff className="w-4 h-4 text-orange-500" /> : <Eye className="w-4 h-4" />}
                      Анонимность: {acc.mask_client_names ? 'ВКЛ' : 'ВЫКЛ'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {accounts.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-muted-foreground">
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
          <div className="bg-card rounded-xl shadow-xl max-w-lg w-full overflow-hidden flex flex-col">
            <div className="p-6 border-b border-border bg-background flex justify-between items-center">
              <h3 className="text-lg font-semibold text-foreground">Персональные задачи для Админа</h3>
              <button onClick={() => setShowChecklistModal(null)} className="text-gray-400 hover:text-muted-foreground">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="p-6">
              <p className="text-sm text-muted-foreground mb-4">Напишите список задач (по одной на каждой строке), которые админ должен выполнить при работе с этим аккаунтом перед выдачей кандидату.</p>
              <textarea
                value={checklistText}
                onChange={e => setChecklistText(e.target.value)}
                className="w-full h-48 border border-gray-300 rounded-lg p-3 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Например:
Сменить пароль
Отписать куратору"
              />
            </div>
            <div className="p-4 bg-background flex justify-end gap-3 border-t border-border">
              <button onClick={() => setShowChecklistModal(null)} className="px-4 py-2 bg-card border border-gray-300 rounded-lg text-sm font-medium hover:bg-background">Отмена</button>
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
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
              >
                {savingChecklist ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-card rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Подключение Telegram аккаунта</h3>
            
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
                  <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 bg-muted rounded-lg hover:bg-gray-200">Отмена</button>
                  <button type="submit" disabled={loading} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50">
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
                  <button type="button" onClick={() => setAuthStep(1)} className="px-4 py-2 bg-muted rounded-lg hover:bg-gray-200">Назад</button>
                  <button type="submit" disabled={loading} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50">
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
                  <button type="button" onClick={() => setAuthStep(2)} className="px-4 py-2 bg-muted rounded-lg hover:bg-gray-200">Назад</button>
                  <button type="submit" disabled={loading} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50">
                    {loading ? 'Проверка...' : 'Войти'}
                  </button>
                </div>
              </form>
            )}

          </div>
        </div>
      )}
    
      {showHistoryModal !== null && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-foreground">История назначений аккаунта</h3>
              <button onClick={() => setShowHistoryModal(null)} className="text-muted-foreground hover:text-foreground">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>
            
            {accountHistory.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">История пуста</p>
            ) : (
              <div className="space-y-4">
                {accountHistory.map((h, i) => (
                  <div key={i} className="flex flex-col sm:flex-row sm:justify-between p-4 bg-muted rounded-lg border border-border">
                    <div>
                      <p className="font-medium text-foreground">Воркер ID: {h.worker_id || 'Неизвестно'}</p>
                      <p className="text-sm text-muted-foreground mt-1">Причина отвязки: {h.reason || 'Активен'}</p>
                    </div>
                    <div className="mt-2 sm:mt-0 text-left sm:text-right text-sm">
                      <p className="text-foreground">Назначен: {new Date(h.assigned_at).toLocaleString()}</p>
                      <p className="text-muted-foreground">Снят: {h.revoked_at ? new Date(h.revoked_at).toLocaleString() : 'По сей день'}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
