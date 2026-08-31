'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus } from 'lucide-react';

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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">Администраторы и Финансисты</h2>
        
        {user?.role === 'OWNER' && (
          <button 
            onClick={() => setIsModalOpen(true)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
          >
            <Plus className="h-4 w-4 mr-2" />
            Добавить
          </button>
        )}
      </div>

      <div className="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Загрузка...</div>
        ) : users.length === 0 ? (
          <div className="p-8 text-center text-gray-500">Пользователи не найдены</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Имя</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Роль</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Куратор</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                  {user?.role === 'OWNER' && (
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map(u => {
                  const assignedCurator = curators.find(c => c.id === u.curator_id);
                  return (
                    <tr key={u.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">#{u.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{u.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                          {u.role === 'FINANCE' ? 'Финансист' : 'Админ'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{u.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user?.role === 'OWNER' ? (
                          <select 
                            value={u.curator_id || ''}
                            onChange={(e) => handleCuratorChange(u.id, e.target.value)}
                            className="font-medium text-gray-900 text-sm border-gray-300 rounded-md py-1 pl-2 pr-8 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
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

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Новый сотрудник</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Имя</label>
                <input 
                  type="text" required 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input 
                  type="email" required 
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Пароль</label>
                <input 
                  type="password" required 
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Роль</label>
                <select 
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
                >
                  <option value="ADMIN">Администратор</option>
                  <option value="FINANCE">Финансист</option>
                </select>
              </div>
              {user?.role === 'OWNER' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Куратор (опционально)</label>
                  <select 
                    value={formData.curator_id}
                    onChange={(e) => setFormData({...formData, curator_id: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
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
    </div>
  );
}
