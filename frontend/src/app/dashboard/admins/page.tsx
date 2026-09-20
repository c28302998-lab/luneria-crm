'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, DollarSign } from 'lucide-react';

export default function AdminsPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<any[]>([]);
  const [curators, setCurators] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    curator_id: '',
    role: 'ADMIN'
  });

  const [isBalanceModalOpen, setIsBalanceModalOpen] = useState(false);
  const [selectedAdmin, setSelectedAdmin] = useState<any>(null);
  const [balanceAmount, setBalanceAmount] = useState('');
  const [payoutDate, setPayoutDate] = useState('');

  const fetchUsers = async () => {
    try {
      const { data } = await api.get('/users/');
      setUsers(data.filter((u: any) => u.role === 'ADMIN' || u.role === 'FINANCE'));
      setCurators(data.filter((u: any) => u.role === 'CURATOR'));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/users/', {
        ...formData,
        curator_id: formData.curator_id ? parseInt(formData.curator_id) : null
      });
      setIsModalOpen(false);
      setFormData({ name: '', email: '', password: '', curator_id: '', role: 'ADMIN' });
      fetchUsers();
    } catch (err) {
      console.error(err);
      alert('Ошибка при создании пользователя');
    }
  };

  const handleBlock = async (id: number, currentStatus: string) => {
    if (!confirm('Вы уверены?')) return;
    try {
      await api.put(`/users/${id}`, {
        status: currentStatus === 'ACTIVE' ? 'BLOCKED' : 'ACTIVE'
      });
      fetchUsers();
    } catch (err) {
      console.error(err);
      alert('Ошибка при изменении статуса');
    }
  };

  const handleCuratorChange = async (userId: number, curatorId: string) => {
    try {
      await api.put(`/users/${userId}`, {
        curator_id: curatorId ? parseInt(curatorId) : null
      });
      fetchUsers();
    } catch (err) {
      console.error(err);
      alert('Ошибка при назначении куратора');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return;
    try {
      await api.delete(`/users/${id}`);
      fetchUsers();
    } catch (err) {
      console.error(err);
      alert('Ошибка при удалении');
    }
  };

  const handleAddBalance = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAdmin) return;
    try {
      await api.post(`/users/${selectedAdmin.id}/add-balance`, {
        amount: parseFloat(balanceAmount),
        payout_date: payoutDate || null
      });
      setIsBalanceModalOpen(false);
      setSelectedAdmin(null);
      setBalanceAmount('');
      setPayoutDate('');
      fetchUsers();
    } catch (err) {
      console.error(err);
      alert('Ошибка при начислении баланса');
    }
  };

  const openBalanceModal = (admin: any) => {
    setSelectedAdmin(admin);
    setBalanceAmount('');
    setPayoutDate(admin.payout_date || '');
    setIsBalanceModalOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-foreground">Администраторы и Финансисты</h2>
        
        {user?.role === 'OWNER' && (
          <button 
            onClick={() => setIsModalOpen(true)}
            className="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition"
          >
            <Plus className="h-4 w-4 mr-2" />
            Добавить
          </button>
        )}
      </div>

      <div className="bg-card shadow-sm rounded-xl border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Загрузка...</div>
        ) : users.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">Пользователи не найдены</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-background">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Имя</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Роль</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Баланс</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Куратор</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Статус</th>
                  {user?.role === 'OWNER' && (
                    <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
                {users.map(u => {
                  const assignedCurator = curators.find(c => c.id === u.curator_id);
                  return (
                    <tr key={u.id} className="hover:bg-background">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">#{u.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-foreground">{u.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-primary/20 text-primary-foreground">
                          {u.role === 'FINANCE' ? 'Финансист' : 'Админ'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">{u.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-foreground">${u.balance || 0}</span>
                          {user?.role === 'OWNER' && u.role === 'ADMIN' && (
                            <button 
                              onClick={() => openBalanceModal(u)}
                              className="p-1 hover:bg-muted rounded text-primary transition-colors"
                              title="Начислить баланс"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                        {u.payout_date && (
                          <div className="text-[10px] text-muted-foreground mt-1">До {new Date(u.payout_date).toLocaleDateString()}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                        {user?.role === 'OWNER' ? (
                          <select 
                            value={u.curator_id || ''}
                            onChange={(e) => handleCuratorChange(u.id, e.target.value)}
                            className="font-medium text-foreground text-sm border-gray-300 rounded-md py-1 pl-2 pr-8 focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
                          >
                            <option value="">Не назначен</option>
                            {curators.map(c => (
                              <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                          </select>
                        ) : (
                          assignedCurator ? assignedCurator.name : 'Не назначен'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          u.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {u.status}
                        </span>
                      </td>
                      {user?.role === 'OWNER' && (
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button 
                            onClick={() => handleBlock(u.id, u.status)}
                            className={`${u.status === 'ACTIVE' ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'}`}
                          >
                            {u.status === 'ACTIVE' ? 'Заблокировать' : 'Разблокировать'}
                          </button>
                          {user?.role === 'OWNER' && (
                            <button 
                              onClick={() => handleDelete(u.id)}
                              className="ml-4 text-red-600 hover:text-red-900"
                            >
                              Удалить
                            </button>
                          )}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Модалка добавления администратора */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">Новый сотрудник</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground">Имя</label>
                <input 
                  type="text" required 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="mt-1 block w-full rounded-md border-border bg-background border p-2 text-sm text-foreground focus:border-primary focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground">Email</label>
                <input 
                  type="email" required 
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="mt-1 block w-full rounded-md border-border bg-background border p-2 text-sm text-foreground focus:border-primary focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground">Пароль</label>
                <input 
                  type="password" required 
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="mt-1 block w-full rounded-md border-border bg-background border p-2 text-sm text-foreground focus:border-primary focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground">Роль</label>
                <select 
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  className="mt-1 block w-full rounded-md border-border bg-background border p-2 text-sm text-foreground focus:border-primary focus:outline-none"
                >
                  <option value="ADMIN">Администратор</option>
                  <option value="FINANCE">Финансист</option>
                </select>
              </div>
              {user?.role === 'OWNER' && (
                <div>
                  <label className="block text-sm font-medium text-muted-foreground">Куратор (опционально)</label>
                  <select 
                    value={formData.curator_id}
                    onChange={(e) => setFormData({...formData, curator_id: e.target.value})}
                    className="mt-1 block w-full rounded-md border-border bg-background border p-2 text-sm text-foreground focus:border-primary focus:outline-none"
                  >
                    <option value="">Без куратора</option>
                    {curators.map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              )}
              <div className="flex justify-end space-x-3 mt-6">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-border rounded-md text-sm font-medium text-muted-foreground hover:bg-background"
                >
                  Отмена
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-primary border border-transparent rounded-md text-sm font-medium text-primary-foreground hover:bg-primary/90"
                >
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модалка начисления баланса */}
      {isBalanceModalOpen && selectedAdmin && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-xl shadow-xl w-full max-w-sm p-6">
            <h3 className="text-lg font-medium text-foreground mb-1">Начислить баланс</h3>
            <p className="text-sm text-muted-foreground mb-4">Для {selectedAdmin.name}</p>
            <form onSubmit={handleAddBalance} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground">Сумма добавления ($)</label>
                <input 
                  type="number" required step="0.01"
                  value={balanceAmount}
                  placeholder="Например: 150.50"
                  onChange={(e) => setBalanceAmount(e.target.value)}
                  className="mt-1 block w-full rounded-md border-border bg-background border p-2 text-sm text-foreground focus:border-primary focus:outline-none" 
                />
                <p className="text-xs text-muted-foreground mt-1">Текущий баланс: ${selectedAdmin.balance || 0}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground">Новая дата выплаты (опционально)</label>
                <input 
                  type="date"
                  value={payoutDate}
                  onChange={(e) => setPayoutDate(e.target.value)}
                  className="mt-1 block w-full rounded-md border-border bg-background border p-2 text-sm text-foreground focus:border-primary focus:outline-none" 
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button 
                  type="button" 
                  onClick={() => setIsBalanceModalOpen(false)}
                  className="px-4 py-2 border border-border rounded-md text-sm font-medium text-muted-foreground hover:bg-background"
                >
                  Отмена
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-primary border border-transparent rounded-md text-sm font-medium text-primary-foreground hover:bg-primary/90"
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
