'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ArrowLeft, UserCircle } from 'lucide-react';
import { MessageCircle } from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/store/auth';

interface Worker {
  id: number;
  status: string;
  created_at: string;
  candidate_id: number;
  admin_id: number;
  partner_id: number | null;
  referrer_id: number | null;
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
const STATUS_LABELS: Record<string, string> = {
  ACTIVE: 'Активен',
  ON_LEAVE: 'В отпуске',
  TERMINATED: 'Уволен'
};

export default function WorkerDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [worker, setWorker] = useState<Worker | null>(null);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [admins, setAdmins] = useState<AdminUser[]>([]);
  const [allWorkers, setAllWorkers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');

  const fetchData = async () => {
    try {
      const [{ data: wData }, { data: pData }, { data: uData }, { data: cData }, { data: allWData }] = await Promise.all([
        api.get(`/workers/${id}`),
        api.get('/partners/'),
        api.get('/users/'),
        api.get(`/comments/worker/${id}`).catch(() => ({ data: [] })),
        api.get('/workers/')
      ]);
      setWorker(wData);
      setPartners(pData);
      setAdmins(uData.filter((u: any) => u.role === 'ADMIN'));
      setComments(cData);
      setAllWorkers(allWData);
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


  const handleReferrerChange = async (newReferrerId: string) => {
    if (!worker) return;
    try {
      await api.patch(`/workers/${worker.id}`, { referrer_id: newReferrerId ? parseInt(newReferrerId) : null });
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при смене реферера.');
    }
  };

  const handleAdminChange = async (newAdminId: string) => {
    if (!worker) return;
    try {
      await api.patch(`/workers/${worker.id}/admin`, null, { params: { admin_id: newAdminId } });
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при изменении администратора. Убедитесь, что у вас есть права.');
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

    const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Удалить заметку?')) return;
    try {
      await api.delete(`/comments/${commentId}`);
      const { data } = await api.get(`/comments/worker/${id}`);
      setComments(data);
    } catch (err) {
      alert('Ошибка при удалении заметки');
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      await api.post(`/comments/worker/${id}`, { text: newComment });
      setNewComment('');
      const { data } = await api.get(`/comments/worker/${id}`);
      setComments(data);
    } catch (err) {
      alert('Ошибка при добавлении комментария');
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
                        className={`px-3 py-1 border rounded-full text-sm font-medium focus:outline-none cursor-pointer ${
              worker.status === 'ACTIVE' ? 'bg-green-50 text-green-800 border-green-200' :
              worker.status === 'TERMINATED' ? 'bg-red-50 text-red-800 border-red-200' :
              'bg-gray-50 text-gray-800 border-gray-200'
            }`}
          >
            {STATUSES.map(s => (
              <option key={s} value={s}>{STATUS_LABELS[s] || s}</option>
            ))}
          </select>
        ) : (
          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
            {STATUS_LABELS[worker.status] || worker.status}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Информация о работнике</h3>
          <div className="space-y-4">

            {isOwner && (
              <div className="flex justify-between items-center border-b border-gray-100 pb-2">
                <span className="text-gray-500 text-sm">Кто привел (Реферер):</span>
                <select 
                  value={worker.referrer_id || ''}
                  onChange={(e) => handleReferrerChange(e.target.value)}
                  className="font-medium text-gray-900 text-sm border-gray-300 rounded-md py-1 pl-2 pr-8 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                >
                  <option value="">-- Никто --</option>
                  {allWorkers.filter(w => w.id !== worker.id).map(w => (
                    <option key={w.id} value={w.id}>Работник #{w.id}</option>
                  ))}
                </select>
              </div>
            )}

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
              {isOwner ? (
                <select 
                  value={worker.admin_id || ''}
                  onChange={(e) => handleAdminChange(e.target.value)}
                  className="font-medium text-gray-900 text-sm border-gray-300 rounded-md py-1 pl-2 pr-8 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                >
                  {admins.map(a => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))}
                </select>
              ) : (
                <span className="font-medium text-gray-900 text-sm">
                  {adminAssigned ? adminAssigned.name : `Пользователь #${worker.admin_id}`}
                </span>
              )}
            </div>
            {isOwner && (
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
            )}
            <div className="flex justify-between">
              <span className="text-gray-500 text-sm">Дата перевода:</span>
              <span className="font-medium text-gray-900 text-sm">{new Date(worker.created_at).toLocaleDateString('ru-RU')}</span>
            </div>
          </div>
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <MessageCircle className="w-5 h-5 mr-2 text-gray-400" />
          Внутренние заметки
        </h3>
        
        <div className="space-y-4 mb-6 max-h-[300px] overflow-y-auto pr-2">
          {comments.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">Нет заметок. Будьте первым!</p>
          ) : (
            comments.map(c => (
              <div key={c.id} className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                <div className="flex justify-between items-start mb-1">
                  <span className="font-semibold text-sm text-gray-900">{c.user?.name || `Пользователь #${c.user_id}`}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-400">{new Date(c.created_at).toLocaleString('ru-RU')}</span>
                    {user?.role === 'OWNER' && (
                      <button onClick={() => handleDeleteComment(c.id)} className="text-red-500 hover:text-red-700 text-xs">Удалить</button>
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{c.text}</p>
              </div>
            ))
          )}
        </div>
        
        <form onSubmit={handleAddComment} className="flex space-x-2">
          <input 
            type="text" 
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Написать заметку (видна только команде)..."
            className="flex-1 rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition">
            Сохранить
          </button>
        </form>
      </div>

    </div>
  );
}
