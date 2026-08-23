'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Users, UserCheck, Briefcase, DollarSign } from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function AnalyticsPage() {
  const [stats, setStats] = useState({
    candidates: 0,
    workers: 0,
    partners: 0,
    users: 0,
  });
  
  const [chartData, setChartData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [candRes, workRes, partRes, userRes] = await Promise.all([
          api.get('/candidates/'),
          api.get('/workers/'),
          api.get('/partners/'),
          api.get('/users/')
        ]);
        
        setStats({
          candidates: candRes.data.length,
          workers: workRes.data.length,
          partners: partRes.data.length,
          users: userRes.data.length,
        });

        // Calculate Monthly Data
        const months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
        const currentMonth = new Date().getMonth();
        const labels = [];
        const candidateCounts = [];
        const workerCounts = [];
        
        // Show last 6 months
        for (let i = 5; i >= 0; i--) {
          let m = currentMonth - i;
          let yearOffset = 0;
          if (m < 0) {
            m += 12;
            yearOffset = -1;
          }
          labels.push(months[m]);
          
          const targetYear = new Date().getFullYear() + yearOffset;
          const targetMonth = m;
          
          const monthCandidates = candRes.data.filter((c: any) => {
            const d = new Date(c.created_at);
            return d.getMonth() === targetMonth && d.getFullYear() === targetYear;
          }).length;
          
          const monthWorkers = workRes.data.filter((w: any) => {
            const d = new Date(w.created_at);
            return d.getMonth() === targetMonth && d.getFullYear() === targetYear;
          }).length;
          
          candidateCounts.push(monthCandidates);
          workerCounts.push(monthWorkers);
        }
        
        setChartData({
          labels,
          datasets: [
            {
              label: 'Новые кандидаты',
              data: candidateCounts,
              backgroundColor: 'rgba(59, 130, 246, 0.5)',
            },
            {
              label: 'Переведены в работники',
              data: workerCounts,
              backgroundColor: 'rgba(16, 185, 129, 0.5)',
            }
          ]
        });

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">Аналитика</h2>
      
      {loading ? <p className="text-gray-500">Загрузка данных...</p> : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Всего Кандидатов</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.candidates}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-3 bg-green-100 rounded-lg">
                  <Briefcase className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Работников</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.workers}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <UserCheck className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Партнеров</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.partners}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-3 bg-orange-100 rounded-lg">
                  <DollarSign className="h-6 w-6 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Сотрудников (CRM)</p>
                  <p className="text-2xl font-semibold text-gray-900">{stats.users}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-96">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Воронка конверсии (последние 6 месяцев)</h3>
            {chartData && (
              <div className="relative h-72 w-full">
                <Bar 
                  data={chartData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'top' as const },
                    }
                  }} 
                />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
