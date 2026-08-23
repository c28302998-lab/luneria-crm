'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, CheckCircle, Clock, Search, Upload, FileText } from 'lucide-react';

interface Task {
  id: number;
  title: string;
  description: string;
  priority: string;
  deadline: string | null;
  status: string;
  assigned_user_id: number;
  files?: string[];
}

export default function TasksPage() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assigned_user_id: '',
    priority: 'MEDIUM',
    deadline: ''
  });

  const fetchData = async () => {
    try {
      const [tasksRes, usersRes] = await Promise.all([
        api.get('/tasks/'),
        api.get('/users/')
      ]);
      setTasks(tasksRes.data);
      setUsers(usersRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.assigned_user_id) return;
    try {
      await api.post('/tasks/', {
        ...formData,
        assigned_user_id: parseInt(formData.assigned_user_id),
        deadline: formData.deadline ? new Date(formData.deadline).toISOString() : null
      });
      setIsModalOpen(false);
      setFormData({ title: '', description: '', assigned_user_id: '', priority: 'MEDIUM', deadline: '' });
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при создании задачи');
    }
  };

  const handleComplete = async (taskId: number) => {
    try {
      await api.put(`/tasks/${taskId}`, { status: 'COMPLETED' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  }


  const handleFileUpload = async (taskId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/tasks/${taskId}/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при загрузке файла');
    }
  };

  const getAssigneeName = (id: number) => {
    const assignedUser = users.find(u => u.id === id);
    return assignedUser ? assignedUser.name : `Пользователь #${id}`;
  };

  const now = new Date();
  const overdueTasks = tasks.filter(t => t.deadline && new Date(t.deadline) < now && t.status !== 'COMPLETED');
  const activeTasks = tasks.filter(t => !t.deadline || new Date(t.deadline) >= now || t.status === 'COMPLETED');

  const renderTaskCard = (task: Task) => {
    const isOverdue = task.deadline && new Date(task.deadline) < now && task.status !== 'COMPLETED';
    const filteredTasks = tasks.filter(t => 
    (statusFilter === 'ALL' || t.status === statusFilter) &&
    (t.title?.toLowerCase().includes(search.toLowerCase()) || t.description?.toLowerCase().includes(search.toLowerCase()))
  );

  return (
      <div key={task.id} className={`bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition ${isOverdue ? 'border-red-300 bg-red-50' : 'border-gray-200'}`}>
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-medium text-gray-900 line-clamp-2">{task.title}</h3>
          <span className={`px-2 py-1 text-xs font-semibold rounded-md ${
            task.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
            task.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
            'bg-blue-100 text-blue-700'
          }`}>
            {task.priority}
          </span>
        </div>
        <p className="text-sm text-gray-500 mb-4 line-clamp-3">{task.description}</p>
        
        <div className="mb-4 text-sm text-gray-600">
          <span className="font-medium">Исполнитель:</span> {getAssigneeName(task.assigned_user_id)}
        </div>

        {task.deadline && (
          <div className={`text-xs mb-3 font-semibold ${isOverdue ? 'text-red-600' : 'text-gray-500'}`}>
            Срок: {new Date(task.deadline).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })}
          </div>
        )}
        
        
          <div className="flex items-center text-xs text-gray-500">
            <Clock className="w-4 h-4 mr-1" />
            {task.status}
          </div>
          
        {task.files && task.files.length > 0 && (
          <div className="mb-4">
            <p className="text-xs font-semibold text-gray-500 mb-2">ПРИКРЕПЛЕННЫЕ ФАЙЛЫ:</p>
            <div className="flex flex-col gap-1">
              {task.files.map((fileUrl: string, idx: number) => {
                const fileName = fileUrl.split('/').pop() || `Файл ${idx+1}`;
                return (
                  <a key={idx} href={api.defaults.baseURL?.replace('/api/v1', '') + fileUrl} target="_blank" rel="noreferrer" className="flex items-center text-xs text-indigo-600 hover:text-indigo-800 bg-indigo-50 p-1.5 rounded-md">
                    <FileText className="w-3 h-3 mr-1" />
                    {fileName.substring(fileName.indexOf('_')+1)}
                  </a>
                );
              })}
            </div>
          </div>
        )}
        
        <div className="flex flex-col gap-2 pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center text-xs text-gray-500">
              <Clock className="w-4 h-4 mr-1" />
              {task.status}
            </div>
            
            <label className="flex items-center cursor-pointer text-xs font-medium text-gray-500 hover:text-indigo-600">
              <Upload className="w-4 h-4 mr-1" />
              Прикрепить
              <input type="file" className="hidden" onChange={(e) => {
                if(e.target.files && e.target.files[0]) handleFileUpload(task.id, e.target.files[0]);
              }} />
            </label>
          </div>
          
          {task.status !== 'COMPLETED' && (
            <button 
              onClick={() => handleComplete(task.id)}
              className="flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-900"
            >
              <CheckCircle className="w-4 h-4 mr-1" />
              Завершить
            </button>
          )}
        </div>
      </div>
    );
  };

  const filteredTasks = tasks.filter(t => 
    (statusFilter === 'ALL' || t.status === statusFilter) &&
    (t.title?.toLowerCase().includes(search.toLowerCase()) || t.description?.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">Задачи</h2>
        
        {(user?.role === 'OWNER' || user?.role === 'CURATOR') && (
          <button 
            onClick={() => setIsModalOpen(true)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
          >
            <Plus className="h-4 w-4 mr-2" />
            Новая задача
          </button>
        )}
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-500">Загрузка...</div>
      ) : filteredTasks.length === 0 ? (
        <div className="p-8 text-center text-gray-500 bg-white rounded-xl shadow-sm border border-gray-200">
          <p>Задач пока нет</p>
        </div>
      ) : (
        <>
          {overdueTasks.length > 0 && (
            <div>
              <h3 className="text-lg font-bold text-red-600 mb-4 flex items-center">
                Пропущенные задачи ({overdueTasks.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {overdueTasks.map(renderTaskCard)}
              </div>
            </div>
          )}
          
          <div>
            <h3 className="text-lg font-bold text-gray-800 mb-4 mt-6">Текущие задачи</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {activeTasks.length > 0 ? activeTasks.map(renderTaskCard) : (
                <div className="col-span-3 text-gray-500">Все текущие задачи выполнены или пропущены.</div>
              )}
            </div>
          </div>
        </>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Новая задача</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Заголовок</label>
                <input 
                  type="text" required 
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Описание</label>
                <textarea 
                  required rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Исполнитель</label>
                <select 
                  required
                  value={formData.assigned_user_id}
                  onChange={(e) => setFormData({...formData, assigned_user_id: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
                >
                  <option value="" disabled>Выберите пользователя...</option>
                  {users.map(u => (
                    <option key={u.id} value={u.id}>{u.name} ({u.role})</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Приоритет</label>
                  <select 
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="LOW">Низкий</option>
                    <option value="MEDIUM">Средний</option>
                    <option value="HIGH">Высокий</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Срок выполнения</label>
                  <input 
                    type="datetime-local"
                    step="60"
                    value={formData.deadline}
                    onChange={(e) => setFormData({...formData, deadline: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
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
