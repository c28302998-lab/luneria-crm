'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Play, Square } from 'lucide-react';

export default function ShiftButton() {
  const { user } = useAuth();
  const [activeShift, setActiveShift] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Only show for ADMIN and CURATOR
  if (!user || (user.role !== 'ADMIN' && user.role !== 'CURATOR')) {
    return null;
  }

  const fetchShift = async () => {
    try {
      const { data } = await api.get('/users/shifts/current');
      setActiveShift(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShift();
  }, []);

  const handleToggle = async () => {
    try {
      if (activeShift) {
        if (!confirm('Завершить текущую смену?')) return;
        await api.post('/users/shifts/end');
        setActiveShift(null);
      } else {
        const { data } = await api.post('/users/shifts/start');
        setActiveShift(data);
      }
    } catch (err) {
      alert('Ошибка при изменении смены');
    }
  };

  if (loading) return <div className="h-9 w-32 bg-gray-100 animate-pulse rounded-md"></div>;

  return (
    <button
      onClick={handleToggle}
      className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
        activeShift 
          ? 'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100' 
          : 'bg-green-50 text-green-700 border border-green-200 hover:bg-green-100'
      }`}
    >
      {activeShift ? (
        <>
          <Square className="w-4 h-4 mr-2 fill-current" />
          Закончить работу
        </>
      ) : (
        <>
          <Play className="w-4 h-4 mr-2 fill-current" />
          Начать работу
        </>
      )}
    </button>
  );
}
