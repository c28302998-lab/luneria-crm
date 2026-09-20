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
const STATUS_LABELS: Record<string, string> = {
  NEW: 'Новый',
  IN_PROGRESS: 'В работе',
  APPROVED: 'Одобрен',
  REJECTED: 'Отказ'
};

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
        headers: { 'Content-Type': undefined }
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


    const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Удалить заметку?')) return;
    try {
      await api.delete(`/comments/${commentId}`);
      const { data } = await api.get(`/comments/candidate/${id}`);
      setComments(data);
    } catch (err) {
      alert('Ошибка при удалении заметки');
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

  if (loading) return <div className="p-8 text-center text-muted-foreground">Загрузка...</div>;
  if (!candidate) return <div className="p-8 text-center text-red-500">Кандидат не найден</div>;

  const canEdit = user?.role === 'OWNER' || (user?.role === 'ADMIN' && candidate.admin_id === user.id);

  const handleConvertToWorker = async () => {
    if (!confirm('Вы уверены, что хотите перевести этого кандидата в Работники? Он появится в разделе "Работники".')) return;
    try {
      const { data } = await api.post('/workers/', { candidate_id: candidate.id });
      if (data.invite_link) {
         prompt('Кандидат успешно переведен в работники! Скопируйте ссылку-приглашение и отправьте работнику для установки пароля:', window.location.origin + data.invite_link);
      } else {
         alert('Кандидат успешно переведен в работники!');
      }
      router.push('/dashboard/workers');
    } catch (err) {
      console.error(err);
      alert('Ошибка при переводе в работники');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/candidates" className="p-2 bg-card border border-border rounded-lg hover:bg-background text-muted-foreground">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h2 className="text-2xl font-semibold text-foreground">{candidate.first_name}</h2>
        
        {canEdit ? (
          <div className="flex items-center space-x-3">
            <select 
              value={candidate.status || 'NEW'}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="px-3 py-1 bg-blue-500/10 text-blue-800 border border-blue-200 rounded-full text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              {STATUSES.map(s => (
                <option key={s} value={s}>{STATUS_LABELS[s] || s}</option>
              ))}
            </select>
            <button 
              onClick={handleConvertToWorker}
              className="px-3 py-1 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition"
            >
              Перевести в работники
            </button>
          </div>
        ) : (
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            {STATUS_LABELS[candidate.status] || candidate.status}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <div className="bg-card rounded-xl shadow-sm border border-border p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">История изменений (Timeline)</h3>
            
            <div className="relative border-l border-border ml-3 space-y-8">
              {candidate.history?.map((event) => (
                <div key={event.id} className="relative pl-6">
                  <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-primary border-2 border-white ring-4 ring-white" />
                  <div className="flex justify-between items-start mb-1">
                    <div className="text-sm font-medium text-foreground">
                      Статус изменен: {event.old_status ? <span className="line-through text-gray-400 mr-1">{event.old_status}</span> : null} 
                      <span className="text-primary">{event.new_status}</span>
                    </div>
                    <time className="text-xs text-muted-foreground flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {new Date(event.created_at).toLocaleString('ru-RU')}
                    </time>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Изменил: {event.user?.name} ({event.user?.role})
                  </p>
                  {event.comment && (
                    <p className="mt-2 text-sm text-gray-700 bg-background p-3 rounded-md border border-border">
                      "{event.comment}"
                    </p>
                  )}
                </div>
              ))}
              
              {!candidate.history?.length && (
                <div className="pl-6 text-sm text-muted-foreground">История пуста.</div>
              )}
            </div>
          </div>
          
          <div className="bg-card rounded-xl shadow-sm border border-border p-6 mt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-foreground">Документы и резюме</h3>
              <label className="cursor-pointer inline-flex items-center px-3 py-1.5 bg-primary/10 text-indigo-700 rounded-md text-sm hover:bg-primary/20 transition">
                <Upload className="h-4 w-4 mr-2" />
                {uploading ? 'Загрузка...' : 'Загрузить файл'}
                <input type="file" className="hidden" onChange={handleFileUpload} disabled={uploading} />
              </label>
            </div>
            {uploadError && <div className="text-red-500 text-sm mb-3">{uploadError}</div>}
            
            <div className="space-y-3">
              {(!candidate.files || candidate.files.length === 0) ? (
                <div className="text-sm text-muted-foreground text-center py-4 border-2 border-dashed border-border rounded-lg">
                  Нет прикрепленных файлов
                </div>
              ) : (
                candidate.files.map((fileUrl, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border border-border rounded-lg bg-background">
                    <div className="flex items-center space-x-3 overflow-hidden">
                      <FileText className="h-5 w-5 text-gray-400 flex-shrink-0" />
                      <span className="text-sm text-gray-700 truncate">{fileUrl.split('/').pop()}</span>
                    </div>
                    <a href={(process.env.NEXT_PUBLIC_API_URL || '') + fileUrl} target="_blank" rel="noreferrer" className="text-gray-400 hover:text-primary transition">
                      <Download className="h-4 w-4" />
                    </a>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-card rounded-xl shadow-sm border border-border p-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wider">Контакты</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Telegram:</span>
                <span className="font-medium text-foreground">{candidate.telegram}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Email:</span>
                <span className="font-medium text-foreground">{candidate.email}</span>
              </div>
            </div>
          </div>
        </div>

        {/* New Application Info Block */}
        {(candidate.experience || candidate.english_level || candidate.desired_income) && (
          <div className="bg-card rounded-xl shadow-sm border border-border p-6 md:col-span-2">
            <h3 className="text-lg font-medium text-foreground mb-4">Анкета с сайта</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {candidate.experience && (
                <div>
                  <span className="text-sm text-muted-foreground block mb-1">Опыт:</span>
                  <p className="font-medium bg-background p-2 rounded-md border border-border">{candidate.experience}</p>
                </div>
              )}
              {candidate.english_level && (
                <div>
                  <span className="text-sm text-muted-foreground block mb-1">Английский:</span>
                  <p className="font-medium bg-background p-2 rounded-md border border-border">{candidate.english_level}</p>
                </div>
              )}
              {candidate.desired_income && (
                <div>
                  <span className="text-sm text-muted-foreground block mb-1">Желаемый доход (1-й месяц):</span>
                  <p className="font-medium bg-background p-2 rounded-md border border-border">{candidate.desired_income}</p>
                </div>
              )}
              <div className="flex gap-4 items-center">
                <div className={`px-3 py-1 text-xs font-semibold rounded-full ${candidate.is_studying ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                  {candidate.is_studying ? 'Учится/работает' : 'Свободен'}
                </div>
                <div className={`px-3 py-1 text-xs font-semibold rounded-full ${candidate.is_longterm ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                  {candidate.is_longterm ? 'Долгосрок' : 'Краткосрок'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="bg-card rounded-xl shadow-sm border border-border p-6 mt-6">
        <h3 className="text-lg font-medium text-foreground mb-4 flex items-center">
          <MessageCircle className="w-5 h-5 mr-2 text-gray-400" />
          Внутренние комментарии
        </h3>
        
        <div className="space-y-4 mb-6 max-h-[300px] overflow-y-auto pr-2">
          {comments.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">Нет комментариев. Будьте первым!</p>
          ) : (
            comments.map(c => (
              <div key={c.id} className="bg-background rounded-lg p-3 border border-border">
                <div className="flex justify-between items-start mb-1">
                  <span className="font-semibold text-sm text-foreground">{c.user?.name || `Пользователь #${c.user_id}`}</span>
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
            placeholder="Написать комментарий (виден только команде)..."
            className="flex-1 rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition">
            Отправить
          </button>
        </form>
      </div>

    </div>
  );
}
