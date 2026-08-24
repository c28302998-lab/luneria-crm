'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ArrowLeft, Clock, Upload, FileText, Download, MessageCircle } from 'lucide-react';
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
  files: string[];
}

const STATUSES = ['NEW', 'IN_PROGRESS', 'APPROVED', 'REJECTED'];

export default function CandidateDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');
  const [statusLoading, setStatusLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    const formData = new FormData();
    formData.append('file', file);
    
    setUploading(true);
    setUploadError('');
    try {
      const res = await api.post(`/candidates/${id}/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // reload candidate
      fetchCandidate();
    } catch (err: any) {
      console.error(err);
      setUploadError('Ошибка загрузки файла');
    } finally {
      setUploading(false);
      // Reset input
      e.target.value = '';
    }
  };

const fetchCandidate = async () => {
    try {
      const candRes = await api.get(`/candidates/${id}`);
      setCandidate(candRes.data);
      try {
        const commRes = await api.get(`/comments/candidate/${id}`);
        setComments(commRes.data);
      } catch (commErr) {
        console.error("Failed to load comments", commErr);
      }
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


  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      await api.post(`/comments/candidate/${id}`, { text: newComment });
      setNewComment('');
      fetchCandidate();
    } catch(err) {
      alert('Ошибка при добавлении комментария');
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
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Документы и резюме</h3>
              <label className="cursor-pointer inline-flex items-center px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-md text-sm hover:bg-indigo-100 transition">
                <Upload className="h-4 w-4 mr-2" />
                {uploading ? 'Загрузка...' : 'Загрузить файл'}
                <input type="file" className="hidden" onChange={handleFileUpload} disabled={uploading} />
              </label>
            </div>
            {uploadError && <div className="text-red-500 text-sm mb-3">{uploadError}</div>}
            
            <div className="space-y-3">
              {(!candidate.files || candidate.files.length === 0) ? (
                <div className="text-sm text-gray-500 text-center py-4 border-2 border-dashed border-gray-200 rounded-lg">
                  Нет прикрепленных файлов
                </div>
              ) : (
                candidate.files.map((fileUrl, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg bg-gray-50">
                    <div className="flex items-center space-x-3 overflow-hidden">
                      <FileText className="h-5 w-5 text-gray-400 flex-shrink-0" />
                      <span className="text-sm text-gray-700 truncate">{fileUrl.split('/').pop()}</span>
                    </div>
                    <a href={process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') + fileUrl} target="_blank" rel="noreferrer" className="text-gray-400 hover:text-indigo-600 transition">
                      <Download className="h-4 w-4" />
                    </a>
                  </div>
                ))
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

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <MessageCircle className="w-5 h-5 mr-2 text-gray-400" />
          Внутренние комментарии
        </h3>
        
        <div className="space-y-4 mb-6 max-h-[300px] overflow-y-auto pr-2">
          {comments.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">Нет комментариев. Будьте первым!</p>
          ) : (
            comments.map(c => (
              <div key={c.id} className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                <div className="flex justify-between items-start mb-1">
                  <span className="font-semibold text-sm text-gray-900">{c.user?.name || `Пользователь #${c.user_id}`}</span>
                  <span className="text-xs text-gray-400">{new Date(c.created_at).toLocaleString('ru-RU')}</span>
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
            placeholder="Написать комментарий (виден только команде)..."
            className="flex-1 rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition">
            Отправить
          </button>
        </form>
      </div>

    </div>
  );
}
