'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import Link from 'next/link';

export default function EmailsPage() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [formData, setFormData] = useState<any>({ email_address: '', app_password: '' });
  const [loading, setLoading] = useState(true);
  const [workers, setWorkers] = useState<any[]>([]);
  const [admins, setAdmins] = useState<any[]>([]);
  const [showHistoryModal, setShowHistoryModal] = useState<number | null>(null);
  const [accountHistory, setAccountHistory] = useState<any[]>([]);

  useEffect(() => {
    fetchAccounts();
    if (user?.role === "OWNER" || user?.role === "ADMIN") fetchWorkers();
  }, []);

  const fetchHistory = async (accId: number) => {
    try {
      // If endpoint doesn't exist yet, we just set empty
      // const { data } = await api.get(`/emails/accounts/${accId}/history`);
      // setAccountHistory(data);
      setAccountHistory([]);
      setShowHistoryModal(accId);
    } catch (e) {
      console.error(e);
      alert("История недоступна");
    }
  };

  const fetchWorkers = async () => {
    try {
      const { data } = await api.get('/users');
      setWorkers(data.filter((u: any) => u.role === 'WORKER'));
      setAdmins(data.filter((u: any) => u.role === 'ADMIN'));
    } catch (e) {}
  };
  
  const fetchAccounts = async () => {
    try {
      const { data } = await api.get('/emails/accounts');
      setAccounts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  
  const handleOpenHistory = async (id: number) => {
    setShowHistoryModal(id);
    try {
      const res = await api.get(`/emails/accounts/${id}/history`);
      setAccountHistory(res.data);
    } catch (e) {
      console.error(e);
      alert('Ошибка при загрузке истории');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот аккаунт?')) return;
    try {
      await api.delete(`/emails/accounts/${id}`);
      fetchAccounts();
    } catch (e: any) {
      alert("Ошибка удаления");
    }
  };

  const handleAssign = async (id: number, field: string, val: any) => {
    try {
      await api.patch(`/emails/accounts/${id}`, { [field]: val || null });
      fetchAccounts();
    } catch (e: any) {
      alert("Ошибка назначения");
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/emails/accounts', formData);
      setShowAdd(false);
      setFormData({ email_address: '', app_password: '' });
      fetchAccounts();
    if (user?.role === "OWNER" || user?.role === "ADMIN") fetchWorkers();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Ошибка добавления аккаунта");
    }
  };

  if (loading) return <div className="p-8">Загрузка...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Почтовые аккаунты</h1>
        {(user?.role === 'OWNER' || user?.role === 'ADMIN') && (
          <button 
            onClick={() => setShowAdd(!showAdd)}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            {showAdd ? 'Отмена' : 'Добавить аккаунт'}
          </button>
        )}
      </div>

      {showAdd && (
        <form onSubmit={handleAdd} className="bg-card p-6 rounded-lg border border-border space-y-4">
          <h2 className="text-xl font-medium">Новый Gmail Аккаунт</h2>
          <p className="text-sm text-gray-500">Внимание: используйте Пароль Приложения (App Password) из настроек безопасности Google, а не основной пароль.</p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email адрес</label>
              <input required type="email" value={formData.email_address} onChange={e => setFormData({...formData, email_address: e.target.value})} className="w-full p-2 rounded border bg-background" placeholder="example@gmail.com" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">App Password</label>
              <input required type="text" value={formData.app_password} onChange={e => setFormData({...formData, app_password: e.target.value})} className="w-full p-2 rounded border bg-background" placeholder="16 букв без пробелов" />
            </div>
          </div>
          <div>
              <label className="block text-sm font-medium mb-1">Назначить работнику</label>
              <select value={(formData as any).assigned_worker_id || ''} onChange={e => setFormData({...formData, assigned_worker_id: e.target.value ? parseInt(e.target.value) : undefined})} className="w-full p-2 rounded border bg-background">
                <option value="">Не назначено</option>
                {workers.map(w => (
                  <option key={w.id} value={w.id}>{w.first_name} {w.last_name} ({w.email})</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Назначить админу</label>
              <select value={(formData as any).assigned_admin_id || ''} onChange={e => setFormData({...formData, assigned_admin_id: e.target.value ? parseInt(e.target.value) : undefined})} className="w-full p-2 rounded border bg-background">
                <option value="">Не назначено</option>
                {admins.map(a => (
                  <option key={a.id} value={a.id}>{a.first_name} {a.last_name} ({a.email})</option>
                ))}
              </select>
            </div>
            <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">Сохранить и проверить</button>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {accounts.map(acc => (
          <div key={acc.id} className="p-6 bg-card rounded-lg border border-border shadow-sm flex flex-col justify-between">
            <div className="flex justify-between items-start">
                <h3 className="font-medium text-lg truncate">{acc.email_address}</h3>
                {(user?.role === 'OWNER' || user?.role === 'ADMIN') && (
                  <button onClick={() => handleDelete(acc.id)} className="text-red-500 hover:text-red-700 text-sm">Удалить</button>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Статус: <span className={acc.status === 'ACTIVE' ? 'text-green-500' : 'text-red-500'}>{acc.status}</span>
              </p>
              
              {(user?.role === 'OWNER' || user?.role === 'ADMIN') ? (
                <div className="mt-3 space-y-2">
                  {user?.role === 'OWNER' && (
                    <div className="flex items-center text-sm">
                      <span className="w-20 text-gray-500">Админ:</span>
                      <select 
                        value={acc.assigned_admin_id || ''} 
                        onChange={e => handleAssign(acc.id, 'assigned_admin_id', e.target.value ? parseInt(e.target.value) : null)}
                        className="flex-1 p-1 text-xs border rounded bg-background"
                      >
                        <option value="">Не назначен</option>
                        {admins.map(a => <option key={a.id} value={a.id}>{a.first_name} ({a.email})</option>)}
                      </select>
                    </div>
                  )}
                  <div className="flex items-center text-sm">
                    <span className="w-20 text-gray-500">Работник:</span>
                    <select 
                      value={acc.assigned_worker_id || ''} 
                      onChange={e => handleAssign(acc.id, 'assigned_worker_id', e.target.value ? parseInt(e.target.value) : null)}
                      className="flex-1 p-1 text-xs border rounded bg-background"
                    >
                      <option value="">Не назначен</option>
                      {workers.map(w => <option key={w.id} value={w.id}>{w.first_name} ({w.email})</option>)}
                    </select>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-500 mt-1">Выдано вам</p>
              )}
            <div className="mt-6">
              <Link href={`/dashboard/emails/${acc.id}`} className="block text-center w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">
                Открыть почту
              </Link>
            </div>
          </div>
        ))}
        {accounts.length === 0 && (
          <div className="col-span-full text-center py-12 text-gray-500 border-2 border-dashed rounded-lg">
            Нет доступных почтовых аккаунтов.
          </div>
        )}
      </div>
    
      {showHistoryModal !== null && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-foreground">История назначений Email</h3>
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
