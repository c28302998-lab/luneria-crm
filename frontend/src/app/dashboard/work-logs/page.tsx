'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Clock, Trash2 } from 'lucide-react';

export default function WorkLogsPage() {
  const { user } = useAuth();
  const [shifts, setShifts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchShifts = async () => {
    try {
      setLoading(true);
      const { data } = await api.get(`/users/shifts/all?target_date=${selectedDate}`);
      setShifts(data);
    } catch (err) {
      console.error('Failed to fetch shifts', err);
    } finally {
      setLoading(false);
    }
  };


  const handleDelete = async (shiftId: number) => {
    if (!confirm('Удалить эту смену?')) return;
    try {
      await api.delete(`/users/shifts/${shiftId}`);
      setShifts(shifts.filter(s => s.id !== shiftId));
    } catch (err) {
      alert('Ошибка при удалении');
      console.error(err);
    }
  };

  useEffect(() => {
    if (user?.role === 'OWNER') {
      fetchShifts();
    }
  }, [user, selectedDate]);

  if (user?.role !== 'OWNER') {
    return <div className="p-8 text-center text-red-500">У вас нет доступа к этой странице</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
          <Clock className="w-6 h-6 text-indigo-600" />
          Учет рабочего времени персонала
        </h1>
        <input 
          type="date" 
          value={selectedDate}
          onChange={e => setSelectedDate(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Загрузка...</div>
        ) : shifts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">Нет записей о сменах на эту дату</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сотрудник</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Роль</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Начало</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Конец</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {shifts.map((shift) => (
                <tr key={shift.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{shift.user?.name}</div>
                    <div className="text-sm text-gray-500">{shift.user?.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {shift.user?.role}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(shift.start_time.endsWith('Z') ? shift.start_time : shift.start_time + 'Z').toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {shift.end_time ? new Date(shift.end_time.endsWith('Z') ? shift.end_time : shift.end_time + 'Z').toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {shift.end_time ? (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-md text-xs font-medium">Завершена</span>
                    ) : (
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded-md text-xs font-medium flex items-center w-max gap-1">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        В работе
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={() => handleDelete(shift.id)}
                      className="text-red-600 hover:text-red-900 transition-colors"
                      title="Удалить смену"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
