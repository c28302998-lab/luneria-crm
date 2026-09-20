'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Loader2, CheckSquare } from 'lucide-react';

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReviews = async () => {
    try {
      const res = await api.get('/reviews/');
      setReviews(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, []);

  const handleSubmit = async (id: number, e: React.FormEvent) => {
    e.preventDefault();
    const fd = new FormData(e.target as HTMLFormElement);
    const potential = fd.get('potential');
    const decision = fd.get('decision');
    const comment = fd.get('comment');
    try {
      await api.post(`/reviews/${id}/submit`, { potential, decision, comment });
      alert('Успешно');
      fetchReviews();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    }
  };

  if (loading) return <div className="flex p-8 justify-center"><Loader2 className="w-8 h-8 animate-spin" /></div>;

  const pending = reviews.filter(r => !r.completed_at);
  const completed = reviews.filter(r => r.completed_at);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-foreground">Аудит аккаунтов (Ревью)</h2>
      
      <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Ожидают проверки</h3>
        {pending.length === 0 ? <p className="text-muted-foreground">Нет активных ревью</p> : (
          <div className="space-y-4">
            {pending.map(r => (
              <form key={r.id} onSubmit={(e) => handleSubmit(r.id, e)} className="bg-muted p-4 rounded-lg flex flex-col gap-4 border border-border">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-lg">Аккаунт ID: {r.account_id}</span>
                  <span className="text-sm text-muted-foreground">Воркер ID: {r.previous_worker_id}</span>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Потенциал аккаунта</label>
                    <select name="potential" required className="w-full rounded-lg bg-card border-border">
                      <option value="HIGH">Высокий</option>
                      <option value="MEDIUM">Средний</option>
                      <option value="LOW">Низкий</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Решение</label>
                    <select name="decision" required className="w-full rounded-lg bg-card border-border">
                      <option value="REASSIGN">Оставить (Переназначить)</option>
                      <option value="RE_REGISTER">На перерегистрацию</option>
                      <option value="ARCHIVE">В архив</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Комментарий</label>
                  <input type="text" name="comment" className="w-full rounded-lg bg-card border-border" placeholder="Причина решения..." />
                </div>
                
                <button type="submit" className="self-end px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium">Завершить ревью</button>
              </form>
            ))}
          </div>
        )}
      </div>

      <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
        <h3 className="text-lg font-bold mb-4">Завершенные ревью</h3>
        {completed.length === 0 ? <p className="text-muted-foreground">Нет завершенных</p> : (
          <div className="space-y-2">
            {completed.map(r => (
              <div key={r.id} className="p-3 bg-muted rounded-lg text-sm flex justify-between border border-border">
                <div>
                  <span className="font-bold">Аккаунт {r.account_id}</span> - {r.decision} (Потенциал: {r.potential})
                  <p className="text-muted-foreground text-xs mt-1">{r.comment}</p>
                </div>
                <div className="text-right text-xs text-muted-foreground">
                  {new Date(r.completed_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
