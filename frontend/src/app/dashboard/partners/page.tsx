'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, Search } from 'lucide-react';

interface Partner {
  id: number;
  company_name: string;
  contact: string;
  country: string;
  seats: number;
  payment_terms: string;
  experience: string;
  registration_time: string;
  response_time: string;
  rating: number;
  last_contact_date: string;
  advances: string;
  schedules: string;
  workers_count: number;
  created_at: string;
}

export default function PartnersPage() {
  const { user } = useAuth();
  const [partners, setPartners] = useState<Partner[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    company_name: '',
    contact: '',
    country: '',
    seats: 0,
    payment_terms: '',
    experience: '',
    registration_time: '',
    response_time: '',
    rating: 0,
    last_contact_date: '',
    advances: '',
    schedules: ''
  });

  const openEditModal = (p: Partner) => {
    setFormData({
      company_name: p.company_name || '',
      contact: p.contact || '',
      country: p.country || '',
      seats: p.seats || 0,
      payment_terms: p.payment_terms || '',
      experience: p.experience || '',
      registration_time: p.registration_time || '',
      response_time: p.response_time || '',
      rating: p.rating || 0,
      last_contact_date: p.last_contact_date || '',
      advances: p.advances || '',
      schedules: p.schedules || ''
    });
    setEditingId(p.id);
    setIsModalOpen(true);
  };


  const fetchPartners = async () => {
    try {
      const { data } = await api.get('/partners/');
      setPartners(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPartners();
  }, []);

  if (user?.role !== 'OWNER') {
    return <div className="p-8 text-center text-red-500 font-semibold">У вас нет доступа к этой странице.</div>;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/partners/${editingId}`, formData);
      } else {
        await api.post('/partners/', formData);
      }
      setIsModalOpen(false);
      setEditingId(null);
      setFormData({ 
        company_name: '', contact: '', country: '', seats: 0, 
        payment_terms: '', experience: '', registration_time: '', 
        response_time: '', rating: 0, last_contact_date: '', advances: '', schedules: '' 
      });
      fetchPartners();
    } catch (err) {
      console.error(err);
      alert('Ошибка при сохранении партнера');
    }
  };

  const handleDelete = async (partnerId: number) => {
    if (!confirm('Вы уверены, что хотите удалить партнера?')) return;
    try {
      await api.delete(`/partners/${partnerId}`);
      fetchPartners();
    } catch (err) {
      console.error(err);
      alert('Ошибка при удалении');
    }
  };

  const filteredPartners = partners.filter(p => 
    p.company_name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-foreground">Партнеры</h2>
        
        <button 
          onClick={() => { setEditingId(null); setFormData({ company_name: '', contact: '', country: '', seats: 0, payment_terms: '', experience: '', registration_time: '', response_time: '', rating: 0, last_contact_date: '', advances: '', schedules: '' }); setIsModalOpen(true); }}
          className="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition"
        >
          <Plus className="h-4 w-4 mr-2" />
          Добавить
        </button>
      </div>

      <div className="bg-card rounded-xl shadow-sm border border-border">
        <div className="p-4 border-b border-border flex space-x-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input 
              type="text" 
              placeholder="Поиск партнеров..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Загрузка...</div>
        ) : filteredPartners.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <p>Партнеры не найдены</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-background">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Агентство</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Контакт</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Страна</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Места</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Оплата</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Опыт</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Регистрация</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Ответ</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Рейтинг</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Посл. контакт</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Авансы</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Графики</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Людей</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
                {filteredPartners.map(p => (
                  <tr key={p.id} className="hover:bg-background">
                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-foreground">{p.company_name}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.contact}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.country}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.seats}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.payment_terms}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.experience}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.registration_time}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.response_time}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.rating}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.last_contact_date}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.advances}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.schedules}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-foreground font-medium">{p.workers_count}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        onClick={() => openEditModal(p)}
                        className="text-indigo-600 hover:text-indigo-900 mr-4"
                      >
                        Изменить
                      </button>
                      <button 
                        onClick={() => handleDelete(p.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Удалить
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-xl shadow-xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-medium text-foreground mb-4">{editingId ? 'Редактировать партнера' : 'Новый партнер'}</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Агентство (Название)</label>
                  <input 
                    type="text" required 
                    value={formData.company_name}
                    onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Контакт (@username или email)</label>
                  <input 
                    type="text" 
                    value={formData.contact}
                    onChange={(e) => setFormData({...formData, contact: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Страна</label>
                  <input 
                    type="text" 
                    value={formData.country}
                    onChange={(e) => setFormData({...formData, country: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Места</label>
                  <input 
                    type="number" 
                    value={formData.seats}
                    onChange={(e) => setFormData({...formData, seats: parseInt(e.target.value) || 0})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Оплата</label>
                  <input 
                    type="text" 
                    placeholder="Например: Base + %"
                    value={formData.payment_terms}
                    onChange={(e) => setFormData({...formData, payment_terms: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Опыт</label>
                  <input 
                    type="text" 
                    placeholder="Например: Да / Нет"
                    value={formData.experience}
                    onChange={(e) => setFormData({...formData, experience: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Регистрация (Время)</label>
                  <input 
                    type="text" 
                    placeholder="Например: 1-2 дня"
                    value={formData.registration_time}
                    onChange={(e) => setFormData({...formData, registration_time: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Ответ</label>
                  <input 
                    type="text" 
                    placeholder="Например: Быстро"
                    value={formData.response_time}
                    onChange={(e) => setFormData({...formData, response_time: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Рейтинг</label>
                  <input 
                    type="number" 
                    value={formData.rating}
                    onChange={(e) => setFormData({...formData, rating: parseFloat(e.target.value) || 0})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Последний контакт</label>
                  <input 
                    type="text" 
                    placeholder="Например: 11.09"
                    value={formData.last_contact_date}
                    onChange={(e) => setFormData({...formData, last_contact_date: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Авансы (Есть ли, когда)</label>
                  <input 
                    type="text" 
                    placeholder="Например: Да, через 2 нед."
                    value={formData.advances}
                    onChange={(e) => setFormData({...formData, advances: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Графики</label>
                  <input 
                    type="text" 
                    placeholder="Например: 2/2, 6/1, Ночные"
                    value={formData.schedules}
                    onChange={(e) => setFormData({...formData, schedules: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-border">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-border rounded-md text-sm font-medium text-muted-foreground hover:bg-background"
                >
                  Отмена
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-primary border border-transparent rounded-md text-sm font-medium text-primary-foreground hover:bg-primary/90"
                >
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
