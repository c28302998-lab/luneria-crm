'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Key, User as UserIcon, Mail } from 'lucide-react';

export default function CRMAccountsPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [passwords, setPasswords] = useState<Record<number, string>>({});
  const [editingUser, setEditingUser] = useState<any>(null);
  
  
  const handleDeleteUser = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return;
    try {
      await api.delete(`/users/${id}`);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при удалении');
    }
  };

  const handleSaveUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    try {
      await api.put(`/users/${editingUser.id}`, {
        name: editingUser.name,
        email: editingUser.email,
        status: editingUser.status
      });
      setEditingUser(null);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка сохранения');
    }
  };

  
  const handleResetPassword = async (userId: number) => {
    if (!confirm('Вы уверены? Старый пароль работника перестанет работать.')) return;
    try {
      const { data } = await api.post(`/users/${userId}/reset-password`);
      setPasswords(prev => ({ ...prev, [userId]: data.password }));
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Ошибка');
    }
  };

  const fetchUsers = async () => {
    try {
      const { data } = await api.get('/users/');
      setUsers(data.filter((u: any) => u.role === 'WORKER'));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === 'OWNER') {
      fetchUsers();
    }
  }, [user]);

  if (user?.role !== 'OWNER') {
    return <div className="p-8 text-center">Доступ закрыт</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground">Аккаунты Работников</h2>
        <p className="text-muted-foreground text-sm mt-1">Здесь отображаются логины для входа в систему ваших работников.</p>
      </div>

      <div className="bg-card shadow-sm rounded-xl border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Загрузка...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-background">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Роль</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Имя</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Email (Логин)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Пароль</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Статус</th>
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
                {users.map((u: any) => (
                  <tr key={u.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">{u.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${u.role === 'OWNER' ? 'bg-red-100 text-red-800' :
                          u.role === 'FINANCE' ? 'bg-yellow-100 text-yellow-800' :
                          u.role === 'CURATOR' ? 'bg-blue-100 text-blue-800' :
                          u.role === 'ADMIN' ? 'bg-indigo-100 text-indigo-800' :
                          'bg-green-100 text-green-800'}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground">
                      {u.name || 'Без имени'}
                    </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground flex items-center">
                      <Mail className="w-3 h-3 mr-2" />
                      {u.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap flex items-center gap-2">
                      <span className="font-mono bg-muted text-foreground px-2 py-1 rounded text-sm select-all">
                        {passwords[u.id] || u.raw_password || '—'}
                      </span>
                      <button 
                        onClick={() => handleResetPassword(u.id)}
                        className="text-xs text-primary hover:text-primary/80 transition-colors border border-primary/20 px-2 py-1 rounded"
                      >
                        Сбросить
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        {u.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button 
                        onClick={() => setEditingUser(u)}
                        className="text-primary hover:underline text-sm font-medium"
                      >
                        Изменить
                      </button>
                      <button 
                        onClick={() => handleDeleteUser(u.id)}
                        className="text-red-500 hover:underline text-sm font-medium ml-4"
                      >
                        Удалить
                      </button>

                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground text-sm">
                      Пользователей не найдено
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button 
                        onClick={() => setEditingUser(u)}
                        className="text-primary hover:underline text-sm font-medium"
                      >
                        Изменить
                      </button>
                      <button 
                        onClick={() => handleDeleteUser(u.id)}
                        className="text-red-500 hover:underline text-sm font-medium ml-4"
                      >
                        Удалить
                      </button>

                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {editingUser && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-md shadow-xl border border-border">
            <h2 className="text-xl font-semibold text-foreground mb-4">Редактировать Аккаунт</h2>
            <form onSubmit={handleSaveUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                <input 
                  type="text" 
                  value={editingUser.name}
                  onChange={e => setEditingUser({...editingUser, name: e.target.value})}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground" 
                  required 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email / Логин</label>
                <input 
                  type="email" 
                  value={editingUser.email}
                  onChange={e => setEditingUser({...editingUser, email: e.target.value})}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground" 
                  required 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Статус</label>
                <select
                  value={editingUser.status}
                  onChange={e => setEditingUser({...editingUser, status: e.target.value})}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground" 
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="BLOCKED">BLOCKED</option>
                  <option value="SUSPENDED">SUSPENDED</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button 
                  type="button" 
                  onClick={() => setEditingUser(null)}
                  className="px-4 py-2 border border-border rounded-lg text-sm text-foreground hover:bg-muted"
                >
                  Отмена
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 shadow"
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
