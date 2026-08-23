'use client';

import { useAuth } from '@/store/auth';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export default function SettingsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  
  const [users, setUsers] = useState<any[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);

  useEffect(() => {
    if (activeTab === 'users' && user?.role === 'OWNER') {
      fetchUsers();
    }
  }, [activeTab]);

  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      const { data } = await api.get('/users/');
      setUsers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingUsers(false);
    }
  };

  const toggleStatus = async (userId: number, currentStatus: string) => {
    try {
      await api.put(`/users/${userId}`, {
        status: currentStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
      });
      fetchUsers();
    } catch (err) {
      console.error(err);
      alert('Ошибка при смене статуса');
    }
  };

  if (!user) return null;

  const tabs = [
    { id: 'profile', label: 'Профиль' },
    ...(user.role === 'OWNER' ? [
      { id: 'users', label: 'Управление пользователями' },
      { id: 'security', label: 'Настройки безопасности' },
      { id: 'roles', label: 'Управление ролями' },
      { id: 'archive', label: 'Архивация' },
    ] : [
      { id: 'notifications', label: 'Уведомления' },
      { id: 'security', label: 'Смена пароля' }
    ])
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">Настройки</h2>
        <p className="mt-1 text-sm text-gray-500">Управление параметрами вашей учетной записи и системы.</p>
      </div>

      <div className="flex space-x-8 border-b border-gray-200">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`pb-4 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id 
                ? 'border-indigo-600 text-indigo-600' 
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="pt-4">
        {activeTab === 'profile' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-2xl">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Информация о профиле</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Имя</label>
                <input 
                  type="text" 
                  disabled
                  value={user.name}
                  className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 border p-2 text-sm text-gray-900" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input 
                  type="email" 
                  disabled
                  value={user.email}
                  className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 border p-2 text-sm text-gray-900" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Роль</label>
                <input 
                  type="text" 
                  disabled
                  value={user.role}
                  className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 border p-2 text-sm text-gray-900" 
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && user.role === 'OWNER' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Все пользователи системы</h3>
              <p className="text-sm text-gray-500">Управление доступом сотрудников (Finance, Admin, Curator).</p>
            </div>
            
            {loadingUsers ? <p className="p-8 text-center text-gray-500">Загрузка...</p> : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Роль</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Имя / Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((u: any) => (
                    <tr key={u.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{u.role}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{u.name}</div>
                        <div className="text-sm text-gray-500">{u.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          u.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {u.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {u.role !== 'OWNER' && (
                          <button 
                            onClick={() => toggleStatus(u.id, u.status)}
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            {u.status === 'ACTIVE' ? 'Заблокировать' : 'Разблокировать'}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'security' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-2xl">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Смена пароля</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Текущий пароль</label>
                <input type="password" placeholder="••••••••" className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Новый пароль</label>
                <input type="password" placeholder="••••••••" className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" />
              </div>
              <button type="button" className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm hover:bg-indigo-700">
                Сохранить
              </button>
            </form>
          </div>
        )}

        {activeTab === 'roles' && user.role === 'OWNER' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-4xl">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Управление ролями и правами</h3>
            <p className="text-sm text-gray-500 mb-6">В системе жестко закодированы базовые роли (RBAC) согласно бизнес-логике. Настроек кастомных ролей на данном этапе (MVP) не предусмотрено.</p>
            
            <div className="space-y-4">
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-indigo-900 mb-2">OWNER (Владелец)</h4>
                <p className="text-sm text-gray-600">Полный доступ ко всем модулям. Может создавать Кураторов, Админов и Финансистов. Только Владелец видит аналитику, финансы (все) и управление ролями.</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-indigo-900 mb-2">CURATOR (Куратор)</h4>
                <p className="text-sm text-gray-600">Может создавать и управлять подчиненными Администраторами. Не имеет доступа к финансам и настройкам безопасности системы.</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-indigo-900 mb-2">ADMIN (Администратор)</h4>
                <p className="text-sm text-gray-600">Добавляет Кандидатов, Работников, ведет переписку. Базовый уровень управления операционной деятельностью.</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-indigo-900 mb-2">FINANCE (Финансист)</h4>
                <p className="text-sm text-gray-600">Имеет доступ только к модулю Финансов (Выплаты) и Отчетам. Не может управлять пользователями.</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'archive' && user.role === 'OWNER' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-4xl">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Архив системы</h3>
            <p className="text-sm text-gray-500 mb-6">Здесь хранятся удаленные (Soft Delete) записи Кандидатов, Работников и Партнеров.</p>
            
            <div className="bg-gray-50 p-8 text-center rounded-lg border border-dashed border-gray-300 flex flex-col items-center justify-center text-gray-400">
              <p>В данный момент корзина архива пуста.</p>
              <p className="text-sm mt-2">При удалении профиля кандидата он попадет сюда, и вы сможете восстановить его.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
