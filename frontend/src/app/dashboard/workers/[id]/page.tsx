'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ArrowLeft, UserCircle } from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/store/auth';

interface Worker {
  id: number;
  status: string;
  created_at: string;
  candidate_id: number;
  admin_id: number;
  partner_id: number | null;
}

interface Partner {
  id: number;
  company_name: string;
}

interface AdminUser {
  id: number;
  name: string;
}

const STATUSES = ['ACTIVE', 'ON_LEAVE', 'TERMINATED'];

export default function WorkerDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [worker, setWorker] = useState<Worker | null>(null);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [admins, setAdmins] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [{ data: wData }, { data: pData }, { data: uData }] = await Promise.all([
        api.get(`/workers/${id}`),
        api.get('/partners/'),
        api.get('/users/')
      ]);
      setWorker(wData);
      setPartners(pData);
      setAdmins(uData.filter((u: any) => u.role === 'ADMIN'));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleStatusChange = async (newStatus: string) => {
    if (!worker || newStatus === worker.status) return;
    try {
      await api.patch(`/workers/${worker.id}/status`, null, { params: { status: newStatus } });
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при изменении статуса. Проверьте права.');
    }
  };

  const handlePartnerChange = async (partnerId: string) => {
    if (!worker) return;
    try {
      await api.patch(`/workers/${worker.id}/partner`, null, { params: { partner_id: partnerId } });
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при назначении партнера. Убедитесь, что у вас есть права.');
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Загрузка...</div>;
  if (!worker) return <div className="p-8 text-center text-red-500">Работник не найден</div>;

  const canEdit = user?.role === 'OWNER' || (user?.role === 'ADMIN' && worker.admin_id === user.id);
  const isOwner = user?.role === 'OWNER';
  const adminAssigned = admins.find(a => a.id === worker.admin_id);
  const partnerAssigned = partners.find(p => p.id === worker.partner_id);

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/workers" className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
          <UserCircle className="w-6 h-6 mr-2 text-gray-400" />
          Работник #{worker.id}
        </h2>
        
        {canEdit ? (
          <select 
            value={worker.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="px-3 py-1 bg-green-50 text-green-800 border border-green-200 rounded-full text-sm font-medium focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer"
          >
            {STATUSES.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        ) : (
          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
            {worker.status}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Информация о работнике</h3>
          <div className="space-y-4">
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span className="text-gray-500 text-sm">ID Кандидата:</span>
              <span className="font-medium text-gray-900 text-sm">
                <Link href={`/dashboard/candidates/${worker.candidate_id}`} className="text-indigo-600 hover:underline">
                  #{worker.candidate_id}
                </Link>
              </span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-100 pb-2">
              <span className="text-gray-500 text-sm">Ответственный Администратор:</span>
              <span className="font-medium text-gray-900 text-sm">
                {adminAssigned ? adminAssigned.name : `Пользователь #${worker.admin_id}`}
              </span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-100 pb-2">
              <span className="text-gray-500 text-sm">Назначенный Партнер:</span>
              {isOwner ? (
                <select 
                  value={worker.partner_id || ''}
                  onChange={(e) => handlePartnerChange(e.target.value)}
                  className="font-medium text-gray-900 text-sm border-gray-300 rounded-md py-1 pl-2 pr-8 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                >
                  <option value="" disabled>Выберите партнера</option>
                  {partners.map(p => (
                    <option key={p.id} value={p.id}>{p.company_name}</option>
                  ))}
                </select>
              ) : (
                <span className="font-medium text-gray-900 text-sm">
                  {partnerAssigned ? partnerAssigned.company_name : 'Не назначен'}
                </span>
              )}
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500 text-sm">Дата перевода:</span>
              <span className="font-medium text-gray-900 text-sm">{new Date(worker.created_at).toLocaleDateString('ru-RU')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
