'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { DollarSign, Check, X, Clock, ExternalLink } from 'lucide-react';

export default function BalanceRequestsPage() {
  const { user } = useAuth();
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRequests = async () => {
    try {
      const { data } = await api.get('/balance-requests/');
      setRequests(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [user]);

  const handleAction = async (id: number, status: 'APPROVED' | 'REJECTED') => {
    if (!confirm(`Вы уверены, что хотите ${status === 'APPROVED' ? 'одобрить' : 'отклонить'}?`)) return;
    try {
      await api.put(`/balance-requests/${id}/status`, { status });
      fetchRequests();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Ошибка');
    }
  };

  if (!['OWNER', 'ADMIN'].includes(user?.role || '')) {
    return <div className="p-8 text-center">Доступ закрыт</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground">Заявки на штрафы и премии</h2>
        <p className="text-muted-foreground text-sm mt-1">
          {user?.role === 'OWNER' 
            ? 'Здесь вы можете одобрять или отклонять штрафы и премии, предложенные администраторами.'
            : 'История ваших запросов на штрафы и премии для воркеров.'}
        </p>
      </div>

      <div className="bg-card shadow-sm rounded-xl border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Загрузка...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-background">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Дата</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Тип</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Работник</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Сумма</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Причина & Пруфы</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Статус</th>
                  {user?.role === 'OWNER' && <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>}
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
                {requests.map((r: any) => (
                  <tr key={r.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${r.type === 'FINE' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                        {r.type === 'FINE' ? 'Штраф' : 'Премия'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                      Воркер #{r.worker_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold">
                      ${r.amount}
                    </td>
                    <td className="px-6 py-4 text-sm text-muted-foreground max-w-xs truncate">
                      <div className="font-medium">{r.reason}</div>
                      {r.proof_url && (
                        <a href={r.proof_url} target="_blank" rel="noreferrer" className="text-primary hover:underline flex items-center mt-1 text-xs">
                          <ExternalLink className="w-3 h-3 mr-1" /> Доказательство
                        </a>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {r.status === 'PENDING' ? (
                        <span className="px-2 inline-flex items-center text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                          <Clock className="w-3 h-3 mr-1" /> Ожидает
                        </span>
                      ) : r.status === 'APPROVED' ? (
                        <span className="px-2 inline-flex items-center text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          <Check className="w-3 h-3 mr-1" /> Одобрено
                        </span>
                      ) : (
                        <span className="px-2 inline-flex items-center text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                          <X className="w-3 h-3 mr-1" /> Отклонено
                        </span>
                      )}
                    </td>
                    {user?.role === 'OWNER' && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {r.status === 'PENDING' ? (
                          <div className="flex space-x-2">
                            <button onClick={() => handleAction(r.id, 'APPROVED')} className="text-green-600 hover:text-green-900 bg-green-50 hover:bg-green-100 px-2 py-1 rounded">Одобрить</button>
                            <button onClick={() => handleAction(r.id, 'REJECTED')} className="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-2 py-1 rounded">Отклонить</button>
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-xs">Обработано</span>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
                {requests.length === 0 && (
                  <tr>
                    <td colSpan={user?.role === 'OWNER' ? 7 : 6} className="px-6 py-8 text-center text-muted-foreground text-sm">
                      Заявок пока нет
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
