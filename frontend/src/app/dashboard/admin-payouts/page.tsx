'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, Trash2, Search, DollarSign } from 'lucide-react';

interface AdminPayout {
  id: number;
  admin_id: number;
  amount: number;
  date: string;
  description: string;
  created_at: string;
}

interface UserAdmin {
  id: number;
  name: string;
  email: string;
  balance: number;
}

export default function AdminPayoutsPage() {
  const { user } = useAuth();
  const [payouts, setPayouts] = useState<AdminPayout[]>([]);
  const [admins, setAdmins] = useState<UserAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    admin_id: '',
    amount: '',
    date: new Date().toISOString().split('T')[0],
    description: ''
  });

  const fetchData = async () => {
    try {
      const [payoutsRes, adminsRes] = await Promise.all([
        api.get('/admin-payouts/'),
        user?.role === 'OWNER' ? api.get('/users/') : Promise.resolve({ data: [] })
      ]);
      setPayouts(payoutsRes.data);
      if (user?.role === 'OWNER') {
        setAdmins(adminsRes.data.filter((u: any) => u.role === 'ADMIN'));
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const targetAdminId = user?.role === 'OWNER' ? formData.admin_id : String(user?.id);
    if (!targetAdminId || !formData.amount || !formData.date) {
      return alert("Заполните все обязательные поля!");
    }
    
    try {
      await api.post('/admin-payouts/', {
        admin_id: parseInt(targetAdminId),
        amount: parseFloat(formData.amount),
        date: formData.date,
        description: formData.description
      });
      setIsModalOpen(false);
      setFormData({ admin_id: '', amount: '', date: new Date().toISOString().split('T')[0], description: '' });
      fetchData();
      alert("Выплата успешно добавлена!");
    } catch (err) {
      console.error(err);
      alert("Ошибка при добавлении выплаты");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Удалить выплату?")) return;
    try {
      await api.delete(`/admin-payouts/${id}`);
      fetchData();
    } catch (err) {
      console.error(err);
      alert("Ошибка при удалении");
    }
  };

  if (loading) return <div className="p-8 text-center text-muted-foreground">Загрузка...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-foreground">{user?.role === 'ADMIN' ? 'Мои выплаты' : 'Выплаты админам'}</h2>
          <p className="text-muted-foreground text-sm mt-1">История балансов и выплат</p>
        </div>
        {(user?.role === 'OWNER' || user?.role === 'FINANCE') && (
          <button 
            onClick={() => setIsModalOpen(true)}
            className="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition shadow-sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Добавить выплату
          </button>
        )}
      </div>

      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-background">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Дата</th>
                {user?.role === 'OWNER' && <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Админ</th>}
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Сумма ($)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Описание</th>
                {user?.role === 'OWNER' && <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {payouts.map(p => {
                const adminName = admins.find(a => a.id === p.admin_id)?.name || 'Админ #' + p.admin_id;
                return (
                  <tr key={p.id} className="hover:bg-background/50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                      {new Date(p.date).toLocaleDateString('ru-RU')}
                    </td>
                    {user?.role === 'OWNER' && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground">
                        {adminName}
                      </td>
                    )}
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-600">
                      + ${p.amount.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">
                      {p.description || '-'}
                    </td>
                    {user?.role === 'OWNER' && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                        <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:text-red-700">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
              {payouts.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                    Нет выплат
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-xl shadow-xl w-full max-w-md border border-border">
            <div className="p-6 border-b border-border flex justify-between items-center">
              <h3 className="text-lg font-medium text-foreground">Добавить выплату админу</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-muted-foreground hover:text-foreground text-2xl leading-none">&times;</button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {user?.role === 'OWNER' ? (
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Администратор *</label>
                  <select
                    required
                    value={formData.admin_id}
                    onChange={e => setFormData({...formData, admin_id: e.target.value})}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">Выберите админа</option>
                    {admins.map(a => (
                      <option key={a.id} value={a.id}>{a.name} (Баланс: ${a.balance})</option>
                    ))}
                  </select>
                </div>
              ) : (
                <input type="hidden" name="admin_id" value={user?.id || ''} />
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Сумма ($) *</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.amount}
                    onChange={e => setFormData({...formData, amount: e.target.value})}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Дата выплаты *</label>
                  <input
                    type="date"
                    required
                    value={formData.date}
                    onChange={e => setFormData({...formData, date: e.target.value})}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Комментарий</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={e => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Бонус за отличную работу..."
                />
              </div>

              <div className="flex justify-end pt-4 space-x-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 border border-border text-foreground rounded-lg hover:bg-background">Отмена</button>
                <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">Добавить</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
