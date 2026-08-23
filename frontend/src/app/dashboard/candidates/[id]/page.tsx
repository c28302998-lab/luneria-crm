'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ArrowLeft, Clock } from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/store/auth';

interface CandidateHistory {
  id: number;
  old_status: string | null;
  new_status: string;
  comment: string | null;
  created_at: string;
  user: {
    name: string;
    role: string;
  };
}

interface Candidate {
  id: number;
  first_name: string;
  telegram: string;
  email: string;
  status: string;
  created_at: string;
  history: CandidateHistory[];
  admin_id: number;
}

const STATUSES = ['NEW', 'IN_PROGRESS', 'APPROVED', 'REJECTED'];

export default function CandidateDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCandidate = async () => {
    try {
      const { data } = await api.get(`/candidates/${id}`);
      setCandidate(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidate();
  }, [id]);

  const handleStatusChange = async (newStatus: string) => {
    if (!candidate || newStatus === candidate.status) return;
    try {
      await api.put(`/candidates/${candidate.id}`, { status: newStatus });
      fetchCandidate(); // Refresh to get new history
    } catch (err) {
      console.error(err);
      alert('Ошибка при изменении статуса. Проверьте права.');
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Загрузка...</div>;
  if (!candidate) return <div className="p-8 text-center text-red-500">Кандидат не найден</div>;

  const canEdit = user?.role === 'OWNER' || (user?.role === 'ADMIN' && candidate.admin_id === user.id);

  const handleConvertToWorker = async () => {
    if (!confirm('Вы уверены, что хотите перевести этого кандидата в Работники? Он появится в разделе "Работники".')) return;
    try {
      await api.post('/workers/', { candidate_id: candidate.id });
      alert('Кандидат успешно переведен в работники!');
      router.push('/dashboard/workers');
    } catch (err) {
      console.error(err);
      alert('Ошибка при переводе в работники');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/candidates" className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h2 className="text-2xl font-semibold text-gray-900">{candidate.first_name}</h2>
        
        {canEdit ? (
          <div className="flex items-center space-x-3">
            <select 
              value={candidate.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="px-3 py-1 bg-blue-50 text-blue-800 border border-blue-200 rounded-full text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              {STATUSES.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <button 
              onClick={handleConvertToWorker}
              className="px-3 py-1 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition"
            >
              Перевести в работники
            </button>
          </div>
        ) : (
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            {candidate.status}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">История изменений (Timeline)</h3>
            
            <div className="relative border-l border-gray-200 ml-3 space-y-8">
              {candidate.history?.map((event) => (
                <div key={event.id} className="relative pl-6">
                  <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-indigo-600 border-2 border-white ring-4 ring-white" />
                  <div className="flex justify-between items-start mb-1">
                    <div className="text-sm font-medium text-gray-900">
                      Статус изменен: {event.old_status ? <span className="line-through text-gray-400 mr-1">{event.old_status}</span> : null} 
                      <span className="text-indigo-600">{event.new_status}</span>
                    </div>
                    <time className="text-xs text-gray-500 flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {new Date(event.created_at).toLocaleString('ru-RU')}
                    </time>
                  </div>
                  <p className="text-sm text-gray-500">
                    Изменил: {event.user?.name} ({event.user?.role})
                  </p>
                  {event.comment && (
                    <p className="mt-2 text-sm text-gray-700 bg-gray-50 p-3 rounded-md border border-gray-100">
                      "{event.comment}"
                    </p>
                  )}
                </div>
              ))}
              
              {!candidate.history?.length && (
                <div className="pl-6 text-sm text-gray-500">История пуста.</div>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-4 uppercase tracking-wider">Контакты</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Telegram:</span>
                <span className="font-medium text-gray-900">{candidate.telegram}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Email:</span>
                <span className="font-medium text-gray-900">{candidate.email}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
