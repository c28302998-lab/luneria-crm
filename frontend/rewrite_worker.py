import json

code = """'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { ArrowLeft, DollarSign, Clock, Activity, Key, CheckCircle2, Circle, FileText, Upload, Download, MessageCircle, ExternalLink, Calendar } from 'lucide-react';
import Link from 'next/link';

export default function WorkerDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [worker, setWorker] = useState<any>(null);
  const [candidate, setCandidate] = useState<any>(null);
  const [userAccount, setUserAccount] = useState<any>(null);
  const [reports, setReports] = useState<any[]>([]);
  const [admin, setAdmin] = useState<any>(null);
  
  const [generatedCreds, setGeneratedCreds] = useState<{email: string, password?: string, message: string} | null>(null);
  
  // Balance requests
  const [fineAmount, setFineAmount] = useState('');
  const [fineReason, setFineReason] = useState('');
  const [fineType, setFineType] = useState('FINE');
  const [fineProofUrl, setFineProofUrl] = useState('');
  const [showFineModal, setShowFineModal] = useState(false);
  const [balanceRequests, setBalanceRequests] = useState<any[]>([]);
  
  // Attendance
  const [attendance, setAttendance] = useState<any>(null);
  const [targetDate, setTargetDate] = useState(new Date().toISOString().split('T')[0]);
  const [accountInfo, setAccountInfo] = useState('');
  const [shiftInfo, setShiftInfo] = useState('');

  // Comments and Files
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');
  const [uploading, setUploading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const { data: wData } = await api.get(`/workers/${id}`);
      setWorker(wData.worker);
      setCandidate(wData.candidate);
      setUserAccount(wData.user_account);
      setReports(wData.reports);
      setAdmin(wData.admin);
      setAccountInfo(wData.worker.account_info || '');
      setShiftInfo(wData.worker.shift || '');

      // Load extra data if we have candidate_id
      if (wData.worker.candidate_id) {
        const [cData, fData, brData] = await Promise.all([
          api.get(`/candidates/${wData.worker.candidate_id}/comments`),
          api.get(`/candidates/${wData.worker.candidate_id}`), // To get files
          api.get(`/balance-requests/`)
        ]);
        setComments(cData.data);
        setCandidate((prev: any) => ({ ...prev, files: fData.data.files }));
        setBalanceRequests(brData.data.filter((r: any) => r.worker_id === wData.user_account?.id));
      }

      // Load attendance for target date
      const { data: attData } = await api.get('/attendance/', { params: { target_date: targetDate } });
      const att = attData.find((a: any) => a.worker_id === wData.worker.id);
      setAttendance(att || null);

    } catch (err: any) {
      if (err.response?.status === 404) {
        router.push('/dashboard/workers');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id, targetDate]);

  const handleCreateAccount = async () => {
    try {
      const { data } = await api.post(`/workers/${id}/create-account`);
      setGeneratedCreds(data);
      fetchData(); // refresh
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка создания аккаунта');
    }
  };

  const handleSubmitFine = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/balance-requests/', {
        worker_id: userAccount.id,
        type: fineType,
        amount: parseFloat(fineAmount),
        reason: fineReason,
        proof_url: fineProofUrl || null
      });
      alert('Заявка отправлена Овнеру на проверку');
      setShowFineModal(false);
      setFineAmount('');
      setFineReason('');
      setFineProofUrl('');
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    }
  };

  const handleInfoChange = async (field: 'account_info' | 'shift', value: string) => {
    try {
      await api.put(`/workers/${id}`, { [field]: value });
    } catch (e) {
      console.error(e);
    }
  };

  const handleAttendanceToggle = async (currentStatus: boolean) => {
    try {
      await api.post('/attendance/', {
        worker_id: parseInt(id as string),
        date: targetDate,
        is_present: !currentStatus
      });
      fetchData();
    } catch (err) {
      alert('Ошибка при сохранении посещаемости');
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !candidate) return;
    try {
      await api.post(`/candidates/${candidate.id}/comments`, { text: newComment });
      setNewComment('');
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !candidate) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    setUploading(true);
    try {
      await api.post(`/candidates/${candidate.id}/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchData();
    } catch (err: any) {
      alert('Ошибка загрузки файла');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  if (loading) return <div className="p-8 text-center">Загрузка...</div>;
  if (!worker) return <div className="p-8 text-center text-red-500">Работник не найден</div>;

  const canEdit = user?.role === 'OWNER' || (user?.role === 'ADMIN' && worker.admin_id === user.id);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center text-sm text-slate-500 mb-4 hover:text-slate-800 transition-colors w-max cursor-pointer" onClick={() => router.back()}>
        <ArrowLeft className="w-4 h-4 mr-1" />
        Назад к списку
      </div>

      {/* HEADER CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-8">
            <h2 className="text-3xl font-bold text-slate-800 mb-2">
              {candidate?.first_name || `Worker #${worker.id}`}
            </h2>
            <div className="flex items-center text-sm text-slate-500 mb-6">
              <Key className="w-4 h-4 mr-1" /> Worker ID #{worker.id}
            </div>
            <div className="grid grid-cols-2 gap-y-4 gap-x-8">
              <div>
                <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Telegram</p>
                <p className="font-medium">{candidate?.telegram || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Email (Логин)</p>
                <p className="font-medium">{candidate?.email || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Админ</p>
                <p className="font-medium">{admin?.name || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Статус</p>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${
                  worker.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {worker.status}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-pink-500 to-purple-600 rounded-2xl shadow-sm p-6 text-white flex flex-col justify-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-10 rounded-full blur-2xl -mr-10 -mt-10"></div>
          <div className="relative z-10 text-center">
            <DollarSign className="w-8 h-8 mx-auto mb-2 opacity-80" />
            <h4 className="text-pink-100 font-medium text-sm uppercase tracking-wider">Текущий Баланс</h4>
            <div className="text-5xl font-extrabold mt-2">
              ${(userAccount?.balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
            {userAccount ? (
              <>
                <p className="text-xs text-pink-200 mt-4">ID Аккаунта: {userAccount.id}</p>
                {canEdit && (
                  <button onClick={() => setShowFineModal(true)} className="mt-4 text-xs bg-white text-purple-700 px-4 py-2 rounded-full font-bold shadow-sm hover:bg-pink-50 transition-colors">
                    Выписать Штраф / Премию
                  </button>
                )}
              </>
            ) : (
              <div className="mt-4 flex flex-col items-center">
                <p className="text-xs text-yellow-200 mb-2">Системный аккаунт еще не создан</p>
                <button onClick={handleCreateAccount} className="text-xs bg-white text-purple-700 px-3 py-1.5 rounded-full font-bold shadow-sm hover:bg-pink-50 transition-colors flex items-center">
                  <Key className="w-3 h-3 mr-1" /> Выдать доступ в CRM
                </button>
              </div>
            )}
            
            {generatedCreds && (
              <div className="absolute inset-0 bg-purple-900/95 backdrop-blur-sm z-20 flex flex-col items-center justify-center p-6 text-left">
                <h4 className="text-white font-bold mb-2 text-center">{generatedCreds.message}</h4>
                {generatedCreds.password && (
                  <div className="w-full bg-black/30 rounded p-3 text-sm space-y-1">
                    <p><span className="text-purple-300">Логин:</span> {generatedCreds.email}</p>
                    <p><span className="text-purple-300">Пароль:</span> <span className="font-mono bg-white/10 px-1 rounded">{generatedCreds.password}</span></p>
                  </div>
                )}
                <p className="text-xs text-purple-200 mt-2 text-center">Скопируйте и передайте работнику.</p>
                <button onClick={() => setGeneratedCreds(null)} className="mt-4 px-4 py-1.5 bg-white/20 hover:bg-white/30 rounded-full text-xs font-bold transition-colors">Закрыть</button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CONTROL SECTION (Учет времени и аккаунты) */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold flex items-center">
              <Calendar className="w-5 h-5 text-indigo-500 mr-2" />
              Управление сценой
            </h3>
            <input 
              type="date" 
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 font-medium"
            />
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-500 mb-1">Рабочий Аккаунт (OF/TG)</label>
              <input 
                type="text"
                placeholder="Название аккаунта"
                value={accountInfo}
                onChange={(e) => setAccountInfo(e.target.value)}
                onBlur={(e) => handleInfoChange('account_info', e.target.value)}
                disabled={!canEdit}
                className="w-full text-sm border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-slate-50 disabled:text-slate-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-500 mb-1">Смена (Киев)</label>
              <input 
                type="text"
                placeholder="10:00 - 18:00"
                value={shiftInfo}
                onChange={(e) => setShiftInfo(e.target.value)}
                onBlur={(e) => handleInfoChange('shift', e.target.value)}
                disabled={!canEdit}
                className="w-full text-sm border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-slate-50 disabled:text-slate-500"
              />
            </div>
            <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-800">Присутствие на смене</p>
                <p className="text-xs text-slate-500">Отметить работника за {targetDate}</p>
              </div>
              <button 
                onClick={() => handleAttendanceToggle(attendance?.is_present)}
                disabled={!canEdit}
                className={`focus:outline-none transition-transform active:scale-95 ${!canEdit ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:opacity-80'}`}
              >
                {attendance?.is_present ? (
                  <CheckCircle2 className="w-10 h-10 text-green-500" />
                ) : (
                  <Circle className="w-10 h-10 text-gray-300 hover:text-gray-400" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* COMMENTS SECTION */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 flex flex-col h-full">
          <div className="flex items-center mb-6">
            <MessageCircle className="w-5 h-5 text-blue-500 mr-2" />
            <h3 className="text-xl font-bold">Внутренние комментарии</h3>
          </div>
          <div className="flex-1 overflow-y-auto min-h-[200px] mb-4 space-y-4 pr-2">
            {comments.length === 0 ? (
              <p className="text-center text-slate-400 text-sm mt-10">Нет комментариев.</p>
            ) : (
              comments.map((c: any) => (
                <div key={c.id} className="bg-slate-50 rounded-xl p-3 border border-slate-100">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-bold text-sm text-slate-800">{c.author.name}</span>
                    <span className="text-xs text-slate-400">{new Date(c.created_at).toLocaleString('ru-RU')}</span>
                  </div>
                  <p className="text-sm text-slate-600 whitespace-pre-wrap">{c.text}</p>
                </div>
              ))
            )}
          </div>
          {canEdit && (
            <div className="flex items-end gap-2 mt-auto">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Добавить комментарий..."
                className="flex-1 text-sm border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500 resize-none"
                rows={2}
              />
              <button 
                onClick={handleAddComment}
                disabled={!newComment.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                Отправить
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* FILES SECTION */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold flex items-center">
              <FileText className="w-5 h-5 text-orange-500 mr-2" />
              Документы и резюме
            </h3>
            {canEdit && (
              <label className="cursor-pointer text-sm font-medium text-orange-600 hover:text-orange-700 bg-orange-50 hover:bg-orange-100 px-4 py-2 rounded-lg flex items-center transition-colors">
                <Upload className="w-4 h-4 mr-2" />
                {uploading ? 'Загрузка...' : 'Загрузить'}
                <input type="file" className="hidden" onChange={handleFileUpload} disabled={uploading} />
              </label>
            )}
          </div>
          {!candidate?.files || candidate.files.length === 0 ? (
            <div className="text-center py-6 border border-dashed border-slate-200 rounded-xl bg-slate-50">
              <p className="text-sm text-slate-400">Нет прикрепленных файлов</p>
            </div>
          ) : (
            <ul className="divide-y divide-slate-100 bg-slate-50 rounded-xl border border-slate-100">
              {candidate.files.map((fileUrl: string, idx: number) => {
                const parts = fileUrl.split('/');
                const fileName = parts[parts.length - 1];
                return (
                  <li key={idx} className="flex items-center justify-between p-3 hover:bg-slate-100 transition-colors rounded-xl">
                    <span className="text-sm font-medium text-slate-700 truncate mr-4">{fileName}</span>
                    <a href={api.defaults.baseURL?.replace('/api/v1', '') + fileUrl} target="_blank" rel="noreferrer" className="text-slate-400 hover:text-orange-500">
                      <Download className="w-4 h-4" />
                    </a>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        {/* REPORTS HISTORY */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 overflow-y-auto max-h-[400px]">
          <div className="flex items-center mb-6">
            <Clock className="w-6 h-6 text-pink-500 mr-2" />
            <h3 className="text-xl font-bold">История Смен</h3>
          </div>
          {reports.length === 0 ? (
            <div className="text-center py-8 text-slate-400 bg-slate-50 rounded-xl border border-dashed">
              <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>Нет отправленных отчетов</p>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((r: any) => (
                <div key={r.id} className="flex justify-between items-center p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-pink-200 transition-colors">
                  <div>
                    <div className="font-bold text-slate-800">Смена #{r.id}</div>
                    <div className="text-sm text-slate-500 mt-1">{new Date(r.created_at).toLocaleString('ru-RU')}</div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-xs text-slate-400 uppercase font-bold tracking-wider mb-1">Выручка</p>
                      <span className="font-bold text-lg text-green-600">${r.amount}</span>
                    </div>
                    <span className={`px-3 py-1 text-xs font-bold rounded-full ${r.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {r.status === 'APPROVED' ? 'Одобрен' : 'Ожидает'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showFineModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-xl font-bold text-foreground mb-4">Заявка на Штраф / Премию</h3>
            <form onSubmit={handleSubmitFine} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Тип</label>
                <select value={fineType} onChange={e => setFineType(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground">
                  <option value="FINE">Штраф</option>
                  <option value="BONUS">Премия</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Сумма ($)</label>
                <input type="number" required min="0.01" step="0.01" value={fineAmount} onChange={e => setFineAmount(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" placeholder="Например: 50" />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Причина</label>
                <textarea required value={fineReason} onChange={e => setFineReason(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" rows={3} placeholder="Подробно опишите причину..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Ссылка на доказательство (Скриншот)</label>
                <input type="url" value={fineProofUrl} onChange={e => setFineProofUrl(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" placeholder="https://..." />
                <p className="text-xs text-muted-foreground mt-1">Загрузите скриншот на любой хостинг (например, imgur) и вставьте ссылку</p>
              </div>
              <div className="flex justify-end space-x-3 pt-4 border-t border-border mt-6">
                <button type="button" onClick={() => setShowFineModal(false)} className="px-4 py-2 text-muted-foreground hover:bg-muted rounded-lg transition-colors">Отмена</button>
                <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors">Отправить заявку</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
"""
with open("src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(code)
