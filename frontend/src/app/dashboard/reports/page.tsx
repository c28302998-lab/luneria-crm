'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, Download, FileText, Trash2 } from 'lucide-react';

export default function ReportsPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
    const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    income: '',
    content: '',
    proof_url: ''
  });

  const handleDelete = async (id: number) => {
    if (!confirm("Точно удалить этот отчет?")) return;
    try {
      await api.delete(`/reports/${id}`);
      fetchReports();
    } catch (e) {
      alert("Ошибка при удалении");
    }
  };

  const fetchReports = async () => {
    try {
      const { data } = await api.get('/reports/');
      setReports(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
            await api.post('/reports/', {
        type: 'DAILY_SUMMARY',
        data: {
          title: formData.title,
          income: formData.income,
          content: formData.content,
          proof_url: formData.proof_url
        }
      });
      setIsModalOpen(false);
      setFormData({ title: '', income: '', content: '', proof_url: '' });
      fetchReports();
    } catch (err) {
      console.error(err);
      alert('Ошибка создания отчета');
    }
  };

  const handleDownload = (report: any) => {
    const textContent = `Отчет #${report.id}\nНазвание: ${report.data?.title || 'Без названия'}\nДата: ${new Date(report.created_at).toLocaleString('ru-RU')}\n\n${report.data?.content || 'Нет содержимого'}`;
    const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${report.id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-foreground">Отчеты</h2>
        <button 
          onClick={() => {
          setFormData({ ...formData, content: `📊 DAILY TEAM REPORT

📅 Дата: 

👥 КОМАНДА

👤 Всего работников: 
🟢 Вышли на смену: 
🔴 Не вышли: 
🆕 Новых работников: 

━━━━━━━━━━━━━━

💰 ФИНАНСОВЫЙ РЕЗУЛЬТАТ

💵 Общий заработок команды за сегодня: $


━━━━━━━━━━━━━━

👤 РЕЗУЛЬТАТЫ ПО РАБОТНИКАМ

1. [Имя]
   📅 Работает с: 
   🟢 Смена: 
   ⏱ 
   💰 Заработал за сегодня: $
   📊 Продаж: 

2. [Имя]
   📅 Работает с: 
   🔴 НЕ ВЫШЕЛ
   Причина: 

━━━━━━━━━━━━━━

🏆 ТОП РЕЗУЛЬТАТЫ

🥇 
🥈 
🥉 

━━━━━━━━━━━━━━

⚠️ НЕ ВЫШЛИ НА СМЕНУ

🔴 

━━━━━━━━━━━━━━

📈 ИТОГО ЗА ДЕНЬ

Общий заработок: $
Работников на смене: 
Не вышли: 

📸 Скрины статистики прикреплены.` });
          setIsModalOpen(true);
        }}
          className="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition"
        >
          <Plus className="h-4 w-4 mr-2" />
          Создать отчет
        </button>
      </div>

      <div className="bg-card rounded-xl shadow-sm border border-border overflow-hidden">
        {loading ? <p className="p-8 text-center text-muted-foreground">Загрузка...</p> : (
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-background">
                            <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Отчет</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Аналитика</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Автор</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Дата</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Действия</th>
              </tr>
            </thead>
            <tbody className="bg-card divide-y divide-border">
              {reports.map((r: any) => (
                <tr key={r.id}>
                                    <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-foreground">{r.data?.title || 'Без названия'}</span>
                      {r.data?.income && <span className="text-xs text-green-600 font-bold mt-1">Доход: ${r.data?.income}</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground max-w-xs truncate">
                    {r.data?.content || '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">Админ #{r.admin_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                    {new Date(r.created_at).toLocaleDateString('ru-RU')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex flex-col items-end space-y-2">
                    {r.data?.proof_url && (
                      <a href={(typeof r.data.proof_url === "string" && r.data.proof_url.startsWith("http")) ? r.data.proof_url : "https://" + r.data.proof_url} target="_blank" rel="noreferrer" className="text-blue-500 hover:text-blue-700 text-xs flex items-center">
                        <FileText className="w-3 h-3 mr-1" /> Пруфы
                      </a>
                    )}
                    <button onClick={() => handleDownload(r)} className="text-primary hover:text-indigo-900 text-xs flex items-center">
                      <Download className="w-3 h-3 mr-1" /> Скачать
                    </button>
                    {(user?.role === 'OWNER' || user?.role === 'ADMIN') && (
                      <button onClick={() => handleDelete(r.id)} className="text-red-500 hover:text-red-700 text-xs flex items-center mt-2">
                        <Trash2 className="w-3 h-3 mr-1" /> Удалить
                      </button>
                    )}
                    </div>
                  </td>
                </tr>
              ))}
              {reports.length === 0 && (
                <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Отчетов пока нет</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-card rounded-xl shadow-xl w-full max-w-md p-6">
                        <h3 className="text-xl font-bold text-foreground mb-4">Ежедневный Отчет Администратора</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Название отчета (Например: Сводка за 09.09)</label>
                <input 
                  type="text" required 
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full border-border bg-card rounded-lg p-2 text-sm focus:ring-primary focus:border-primary" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Общая Выручка команды ($)</label>
                <input 
                  type="number" step="0.01" required 
                  value={formData.income}
                  onChange={(e) => setFormData({...formData, income: e.target.value})}
                  className="w-full border-border bg-card rounded-lg p-2 text-sm focus:ring-primary focus:border-primary" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Аналитика / Комментарий</label>
                <textarea 
                  required rows={20} style={{ fontFamily: 'monospace' }}
                  value={formData.content}
                  placeholder="Воркеры отработали отлично, трафик с TikTok идет хорошо. Воркер №3 просел, провел с ним беседу."
                  onChange={(e) => setFormData({...formData, content: e.target.value})}
                  className="w-full border-border bg-card rounded-lg p-2 text-sm focus:ring-primary focus:border-primary" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Скриншот / Доказательства (Ссылка)</label>
                <input 
                  type="url"
                  placeholder="https://..."
                  value={formData.proof_url}
                  onChange={(e) => setFormData({...formData, proof_url: e.target.value})}
                  className="w-full border-border bg-card rounded-lg p-2 text-sm focus:ring-primary focus:border-primary" 
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-background"
                >
                  Отмена
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-primary border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary/90"
                >
                  Сохранить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
