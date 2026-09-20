'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, TrendingUp, TrendingDown, DollarSign, Upload, FileText } from 'lucide-react';

interface Payment {
  id: number;
  worker_id: number;
  partner_id: number;
  amount: number;
  amount_company: number;
  amount_worker: number;
  amount_admin: number;
  date: string;
  status: string;
  files?: string[];
}

interface Expense {
  id: number;
  reason: string;
  amount: number;
  date: string;
  created_by: number;
  files?: string[];
}

export default function FinancePage() {
  const { user } = useAuth();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [workers, setWorkers] = useState<any[]>([]);
  const [partners, setPartners] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [activeTab, setActiveTab] = useState<'payments' | 'expenses' | 'stats'>('payments');
  
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [paymentData, setPaymentData] = useState({
    worker_id: '',
    amount: '',
    amount_company: '',
    amount_worker: '',
    amount_admin: ''
  });

  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [uploadingPaymentId, setUploadingPaymentId] = useState<number | null>(null);
  const [uploadingExpenseId, setUploadingExpenseId] = useState<number | null>(null);
  const [expenseData, setExpenseData] = useState({
    reason: '',
    amount: ''
  });

  const fetchData = async () => {
    try {
      const [payRes, expRes, statsRes, workRes, partRes] = await Promise.all([
        api.get('/payments/'),
        api.get('/payments/expenses'),
        api.get('/payments/stats'),
        api.get('/workers/'),
        api.get('/partners/')
      ]);
      setPayments(payRes.data);
      setExpenses(expRes.data);
      setStats(statsRes.data);
      setWorkers(workRes.data);
      setPartners(partRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDeletePayment = async (paymentId: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту выплату?')) return;
    try {
      await api.delete(`/payments/${paymentId}`);
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при удалении выплаты');
    }
  };

  const handleDeleteExpense = async (expenseId: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот расход?')) return;
    try {
      await api.delete(`/payments/expenses/${expenseId}`);
      fetchData();
    } catch (err) {
      console.error(err);
      alert('Ошибка при удалении расхода');
    }
  };

  const handleCreatePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!paymentData.worker_id) return alert('Выберите работника');
    try {
      await api.post('/payments/', {
        worker_id: parseInt(paymentData.worker_id),
        amount: parseFloat(paymentData.amount_company) || 0,
        amount_company: parseFloat(paymentData.amount_company) || 0,
        amount_worker: parseFloat(paymentData.amount_worker) || 0,
        amount_admin: parseFloat(paymentData.amount_admin) || 0,
      });
      setIsPaymentModalOpen(false);
      setPaymentData({ worker_id: '', amount: '', amount_company: '', amount_worker: '', amount_admin: '' });
      fetchData();
    } catch (err: any) {
      if (err.response?.data?.detail) {
        alert(`Ошибка: ${err.response.data.detail}`);
      } else {
        alert('Ошибка при создании выплаты. Проверьте данные.');
      }
    }
  };

  const handleCreateExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!expenseData.reason || !expenseData.amount) return;
    try {
      await api.post('/payments/expenses', {
        reason: expenseData.reason,
        amount: parseFloat(expenseData.amount)
      });
      setIsExpenseModalOpen(false);
      setExpenseData({ reason: '', amount: '' });
      fetchData();
    } catch (err: any) {
      console.error("Expense creation error:", err.response?.data || err);
      alert(`Ошибка при создании расхода: ${err.response?.data?.detail || err.message}`);
    }
  };


  const handlePaymentFileUpload = async (id: number, file: File) => {
    setUploadingPaymentId(id);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/payments/${id}/files`, formData, { headers: { 'Content-Type': undefined } });
      fetchData();
    } catch (err) { alert('Ошибка при загрузке чека'); } finally { setUploadingPaymentId(null); }
  };

  const handleExpenseFileUpload = async (id: number, file: File) => {
    setUploadingExpenseId(id);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/payments/expenses/${id}/files`, formData, { headers: { 'Content-Type': undefined } });
      fetchData();
    } catch (err) { alert('Ошибка при загрузке чека'); } finally { setUploadingExpenseId(null); }
  };

  const getPartnerName = (id: number) => partners.find(p => p.id === id)?.company_name || `Партнер #${id}`;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <h2 className="text-2xl font-semibold text-foreground">Финансы</h2>
        <div className="flex space-x-2">
          <button 
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'stats' ? 'bg-primary/10 text-indigo-700' : 'text-muted-foreground hover:bg-background'}`}
          >
            Статистика
          </button>
          <button 
            onClick={() => setActiveTab('payments')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'payments' ? 'bg-primary/10 text-indigo-700' : 'text-muted-foreground hover:bg-background'}`}
          >
            Выплаты (Прибыль)
          </button>
          <button 
            onClick={() => setActiveTab('expenses')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'expenses' ? 'bg-primary/10 text-indigo-700' : 'text-muted-foreground hover:bg-background'}`}
          >
            Расходы (Расстраты)
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-muted-foreground">Загрузка...</div>
      ) : (
        <>
          {activeTab === 'stats' && stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-card p-6 rounded-xl shadow-sm border border-border">
                <div className="flex items-center">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-muted-foreground">Доля компании (Прибыль)</p>
                    <p className="text-2xl font-semibold text-foreground">${stats.company_revenue.toFixed(2)}</p>
                  </div>
                </div>
              </div>
              <div className="bg-card p-6 rounded-xl shadow-sm border border-border">
                <div className="flex items-center">
                  <div className="p-3 bg-red-100 rounded-lg">
                    <TrendingDown className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-muted-foreground">Расходы (Расстраты)</p>
                    <p className="text-2xl font-semibold text-foreground">${stats.total_expenses.toFixed(2)}</p>
                  </div>
                </div>
              </div>
              <div className="bg-card p-6 rounded-xl shadow-sm border border-border">
                <div className="flex items-center">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <DollarSign className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-muted-foreground">Чистая прибыль</p>
                    <p className={`text-2xl font-semibold ${stats.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${stats.net_profit.toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="space-y-4">
              <div className="flex justify-end">
                <button 
                  onClick={() => setIsPaymentModalOpen(true)}
                  className="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition"
                >
                  <Plus className="h-4 w-4 mr-2" /> Добавить прибыль
                </button>
              </div>
              <div className="bg-card rounded-xl shadow-sm border border-border overflow-hidden">
                <table className="min-w-full divide-y divide-border">
                  <thead className="bg-background">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Партнер -&gt; Работник</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Прибыль Компании</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Дата</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Чеки</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Чеки</th>
                      {user?.role === 'OWNER' && (
                        <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Действия</th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-card divide-y divide-border">
                    {payments.map(p => (
                      <tr key={p.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                          <span className="font-medium">{getPartnerName(p.partner_id)}</span>
                          <span className="text-gray-400 mx-2">-&gt;</span>
                          Работник #{p.worker_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-semibold">${p.amount_company}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">{new Date(p.date).toLocaleDateString('ru-RU')}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                          {p.files && p.files.length > 0 && (
                            <div className="flex flex-col gap-1 mb-2">
                              {p.files.map((fileUrl: string, idx: number) => (
                                <a key={idx} href={(api.defaults.baseURL || '') + fileUrl} target="_blank" rel="noreferrer" className="flex items-center text-xs text-primary hover:underline">
                                  <FileText className="w-3 h-3 mr-1" /> Чек {idx+1}
                                </a>
                              ))}
                            </div>
                          )}
                        </td>
                        {user?.role === 'OWNER' && (
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end space-x-3">
                              {uploadingPaymentId === p.id ? (
                                <span className="text-primary flex items-center text-xs"><span className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary mr-1"></span> Загрузка...</span>
                              ) : (
                                <label className="cursor-pointer text-primary hover:text-indigo-900 flex items-center">
                                  <Upload className="w-4 h-4 mr-1" /> Загрузить
                                  <input type="file" className="hidden" onChange={(ev) => {
                                    if(ev.target.files && ev.target.files[0]) handlePaymentFileUpload(p.id, ev.target.files[0]);
                                  }} />
                                </label>
                              )}
                              <button onClick={() => handleDeletePayment(p.id)} className="text-red-600 hover:text-red-900">Удалить</button>
                            </div>
                          </td>
                        )}
                      </tr>
                    ))}
                    {payments.length === 0 && <tr><td colSpan={4} className="text-center p-8 text-muted-foreground">Нет данных</td></tr>}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'expenses' && (
            <div className="space-y-4">
              <div className="flex justify-end">
                <button 
                  onClick={() => setIsExpenseModalOpen(true)}
                  className="flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
                >
                  <Plus className="h-4 w-4 mr-2" /> Добавить расстрату
                </button>
              </div>
              <div className="bg-card rounded-xl shadow-sm border border-border overflow-hidden">
                <table className="min-w-full divide-y divide-border">
                  <thead className="bg-background">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Причина (Описание)</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Сумма</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Дата</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Чеки</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Чеки</th>
                      {user?.role === 'OWNER' && (
                        <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Действия</th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-card divide-y divide-border">
                    {expenses.map(e => (
                      <tr key={e.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">#{e.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground">{e.reason}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-red-600">-${e.amount}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">{new Date(e.date).toLocaleDateString('ru-RU')}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                          {e.files && e.files.length > 0 && (
                            <div className="flex flex-col gap-1 mb-2">
                              {e.files.map((fileUrl: string, idx: number) => (
                                <a key={idx} href={(api.defaults.baseURL || '') + fileUrl} target="_blank" rel="noreferrer" className="flex items-center text-xs text-primary hover:underline">
                                  <FileText className="w-3 h-3 mr-1" /> Чек {idx+1}
                                </a>
                              ))}
                            </div>
                          )}
                        </td>
                        {user?.role === 'OWNER' && (
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end space-x-3">
                              {uploadingExpenseId === e.id ? (
                                <span className="text-primary flex items-center text-xs"><span className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary mr-1"></span> Загрузка...</span>
                              ) : (
                                <label className="cursor-pointer text-primary hover:text-indigo-900 flex items-center">
                                  <Upload className="w-4 h-4 mr-1" /> Загрузить
                                  <input type="file" className="hidden" onChange={(ev) => {
                                    if(ev.target.files && ev.target.files[0]) handleExpenseFileUpload(e.id, ev.target.files[0]);
                                  }} />
                                </label>
                              )}
                              <button onClick={() => handleDeleteExpense(e.id)} className="text-red-600 hover:text-red-900">Удалить</button>
                            </div>
                          </td>
                        )}
                      </tr>
                    ))}
                    {expenses.length === 0 && <tr><td colSpan={4} className="text-center p-8 text-muted-foreground">Нет данных</td></tr>}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Payment Modal */}
      {isPaymentModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-card rounded-xl shadow-xl w-full max-w-lg p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">Новая прибыль (от партнера)</h3>
            <form onSubmit={handleCreatePayment} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Кому (Работник)</label>
                <select 
                  required 
                  value={paymentData.worker_id}
                  onChange={(e) => setPaymentData({...paymentData, worker_id: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none"
                >
                  <option value="" disabled>Выберите работника...</option>
                  {workers.map(w => (
                    <option key={w.id} value={w.id}>
                      Работник #{w.id} (Кандидат #{w.candidate_id}) - Партнер: {getPartnerName(w.partner_id)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Прибыль Компании ($)</label>
                <input 
                  type="number" required step="0.01"
                  value={paymentData.amount_company}
                  onChange={(e) => setPaymentData({...paymentData, amount_company: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm text-green-700 bg-green-50 focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={() => setIsPaymentModalOpen(false)} className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-background">Отмена</button>
                <button type="submit" className="px-4 py-2 bg-primary border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary/90">Провести</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Expense Modal */}
      {isExpenseModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-card rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">Добавить расстрату (расход)</h3>
            <form onSubmit={handleCreateExpense} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Причина (на что потрачено)</label>
                <input 
                  type="text" required 
                  value={expenseData.reason}
                  onChange={(e) => setExpenseData({...expenseData, reason: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-red-500 focus:outline-none" 
                  placeholder="Например: Аренда сервера, реклама..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Сумма ($)</label>
                <input 
                  type="number" required step="0.01"
                  value={expenseData.amount}
                  onChange={(e) => setExpenseData({...expenseData, amount: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-red-500 focus:outline-none" 
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={() => setIsExpenseModalOpen(false)} className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-background">Отмена</button>
                <button type="submit" className="px-4 py-2 bg-red-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-red-700">Добавить</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
