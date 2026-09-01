'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Check, X, Clock, Loader2, MessageSquare } from 'lucide-react';

export default function TelegramRequests() {
  const { user } = useAuth();
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<number | null>(null);

  const fetchRequests = async () => {
    try {
      const { data } = await api.get('/telegram/admin/requests');
      setRequests(data);
    } catch (error) {
      console.error('Failed to fetch requests', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleAction = async (id: number, status: string) => {
    const comment = prompt(`Вы собираетесь изменить статус заявки на ${status}. Опционально, оставьте комментарий для пользователя:`);
    if (comment === null) return;
    
    setProcessing(id);
    try {
      await api.patch(`/telegram/admin/requests/${id}/status`, {
        status,
        owner_comment: comment || null
      });
      fetchRequests();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка обновления заявки');
    } finally {
      setProcessing(null);
    }
  };

  if (loading) return <div className="flex justify-center p-8"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            Заявки Telegram
          </h1>
          <p className="text-sm text-gray-500 mt-1">Запросы на изменение настроек или сессий от администраторов</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Пользователь</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Тип запроса</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Причина</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {requests.map((req) => (
              <tr key={req.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(req.created_at).toLocaleString('ru-RU')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {req.user ? `${req.user.name}` : `ID: ${req.user_id}`}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">
                  {req.request_type}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    req.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                    req.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                    req.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {req.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={req.reason}>
                  {req.reason}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {req.status === 'PENDING' ? (
                    <div className="flex gap-2">
                      <button 
                        onClick={() => handleAction(req.id, 'APPROVED')}
                        disabled={processing === req.id}
                        className="text-green-600 hover:text-green-900 disabled:opacity-50"
                        title="Одобрить"
                      >
                        <Check className="w-5 h-5" />
                      </button>
                      <button 
                        onClick={() => handleAction(req.id, 'REJECTED')}
                        disabled={processing === req.id}
                        className="text-red-600 hover:text-red-900 disabled:opacity-50"
                        title="Отклонить"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  ) : (
                    <span className="text-gray-400 text-xs">Обработано</span>
                  )}
                </td>
              </tr>
            ))}
            {requests.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                  Нет активных заявок
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
