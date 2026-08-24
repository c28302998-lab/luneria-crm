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
        amount: parseFloat(paymentData.amount) || 0,
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
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/payments/${id}/files`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      fetchData();
    } catch (err) { alert('Ошибка при загрузке чека'); }
  };

  const handleExpenseFileUpload = async (id: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/payments/expenses/${id}/files`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      fetchData();
    } catch (err) { alert('Ошибка при загрузке чека'); }
  };

  const getPartnerName = (id: number) => partners.find(p => p.id === id)?.company_name || `Партнер #${id}`;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-gray-200 pb-4">
        <h2 className="text-2xl font-semibold text-gray-900">Финансы</h2>
        <div className="flex space-x-2">
          <button 
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'stats' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-500 hover:bg-gray-50'}`}
          >
            Статистика
          </button>
          <button 
            onClick={() => setActiveTab('payments')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'payments' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-500 hover:bg-gray-50'}`}
          >
            Выплаты (Прибыль)
          </button>
          <button 
            onClick={() => setActiveTab('expenses')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${activeTab === 'expenses' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-500 hover:bg-gray-50'}`}
          >
            Расходы (Расстраты)
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-500">Загрузка...</div>
      ) : (
        <>
          {activeTab === 'stats' && stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Доля компании (Прибыль)</p>
                    <p className="text-2xl font-semibold text-gray-900">${stats.company_revenue.toFixed(2)}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center">
                  <div className="p-3 bg-red-100 rounded-lg">
                    <TrendingDown className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Расходы (Расстраты)</p>
                    <p className="text-2xl font-semibold text-gray-900">${stats.total_expenses.toFixed(2)}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <DollarSign className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Чистая прибыль</p>
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
                  className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
                >
                  <Plus className="h-4 w-4 mr-2" /> Добавить прибыль
                </button>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Партнер -&gt; Работник</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Общая Сумма</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Доля Компании</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Работнику</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Админу</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Чеки</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Чеки</th>
                      {user?.role === 'OWNER' && (
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {payments.map(p => (
                      <tr key={p.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <span className="font-medium">{getPartnerName(p.partner_id)}</span>
                          <span className="text-gray-400 mx-2">-&gt;</span>
                          Работник #{p.worker_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">${p.amount}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-semibold">${p.amount_company}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${p.amount_worker}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${p.amount_admin}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(p.date).toLocaleDateString('ru-RU')}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {p.files && p.files.length > 0 && (
                            <div className="flex flex-col gap-1 mb-2">
                              {p.files.map((fileUrl: string, idx: number) => (
                                <a key={idx} href={(api.defaults.baseURL || '') + fileUrl} target="_blank" rel="noreferrer" className="flex items-center text-xs text-indigo-600 hover:underline">
                                  <FileText className="w-3 h-3 mr-1" /> Чек {idx+1}
                                </a>
                              ))}
                            </div>
                          )}
                        </td>
                        {user?.role === 'OWNER' && (
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end space-x-3">
                              <label className="cursor-pointer text-indigo-600 hover:text-indigo-900 flex items-center">
                                <Upload className="w-4 h-4 mr-1" /> Загрузить
                                <input type="file" className="hidden" onChange={(ev) => {
                                  if(ev.target.files && ev.target.files[0]) handlePaymentFileUpload(p.id, ev.target.files[0]);
                                }} />
                              </label>
                              <button onClick={() => handleDeletePayment(p.id)} className="text-red-600 hover:text-red-900">Удалить</button>
                            </div>
                          </td>
                        )}
                      </tr>
                    ))}
                    {payments.length === 0 && <tr><td colSpan={6} className="text-center p-8 text-gray-500">Нет данных</td></tr>}
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
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Причина (Описание)</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Сумма</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Чеки</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Чеки</th>
                      {user?.role === 'OWNER' && (
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {expenses.map(e => (
                      <tr key={e.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">#{e.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{e.reason}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-red-600">-${e.amount}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(e.date).toLocaleDateString('ru-RU')}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {e.files && e.files.length > 0 && (
                            <div className="flex flex-col gap-1 mb-2">
                              {e.files.map((fileUrl: string, idx: number) => (
                                <a key={idx} href={(api.defaults.baseURL || '') + fileUrl} target="_blank" rel="noreferrer" className="flex items-center text-xs text-indigo-600 hover:underline">
                                  <FileText className="w-3 h-3 mr-1" /> Чек {idx+1}
                                </a>
                              ))}
                            </div>
                          )}
                        </td>
                        {user?.role === 'OWNER' && (
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end space-x-3">
                              <label className="cursor-pointer text-indigo-600 hover:text-indigo-900 flex items-center">
                                <Upload className="w-4 h-4 mr-1" /> Загрузить
                                <input type="file" className="hidden" onChange={(ev) => {
                                  if(ev.target.files && ev.target.files[0]) handleExpenseFileUpload(e.id, ev.target.files[0]);
                                }} />
                              </label>
                              <button onClick={() => handleDeleteExpense(e.id)} className="text-red-600 hover:text-red-900">Удалить</button>
                            </div>
                          </td>
                        )}
                      </tr>
                    ))}
                    {expenses.length === 0 && <tr><td colSpan={4} className="text-center p-8 text-gray-500">Нет данных</td></tr>}
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
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Новая прибыль (от партнера)</h3>
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
                <label className="block text-sm font-medium text-gray-700">Общая сумма прибыли ($)</label>
                <input 
                  type="number" required step="0.01"
                  value={paymentData.amount}
                  onChange={(e) => setPaymentData({...paymentData, amount: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div className="grid grid-cols-3 gap-4 border-t pt-4 mt-2">
                <div>
                  <label className="block text-xs font-medium text-gray-700">Доля Компании (Наша)</label>
                  <input 
                    type="number" required step="0.01"
                    value={paymentData.amount_company}
                    onChange={(e) => setPaymentData({...paymentData, amount_company: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm text-green-700 bg-green-50" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700">Доля Работника</label>
                  <input 
                    type="number" required step="0.01"
                    value={paymentData.amount_worker}
                    onChange={(e) => setPaymentData({...paymentData, amount_worker: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700">Доля Админа</label>
                  <input 
                    type="number" required step="0.01"
                    value={paymentData.amount_admin}
                    onChange={(e) => setPaymentData({...paymentData, amount_admin: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm" 
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={() => setIsPaymentModalOpen(false)} className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">Отмена</button>
                <button type="submit" className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-indigo-700">Провести</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Expense Modal */}
      {isExpenseModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Добавить расстрату (расход)</h3>
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
                <button type="button" onClick={() => setIsExpenseModalOpen(false)} className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">Отмена</button>
                <button type="submit" className="px-4 py-2 bg-red-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-red-700">Добавить</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
