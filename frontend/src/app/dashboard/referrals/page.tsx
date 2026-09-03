'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Users, User, ArrowRight } from 'lucide-react';

export default function ReferralsPage() {
  const { user } = useAuth();
  const [workers, setWorkers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== 'OWNER') return;
    
    const fetchReferrals = async () => {
      try {
        const res = await api.get('/workers/');
        setWorkers(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchReferrals();
  }, [user]);

  if (user?.role !== 'OWNER') {
    return <div className="p-8 text-center text-red-500">Доступ запрещен. Только Владелец может видеть эту страницу.</div>;
  }

  if (loading) return <div className="p-8 text-center">Загрузка реферального дерева...</div>;

  // Build tree
  const roots = workers.filter(w => !w.referrer_id);
  const getChildren = (parentId: number) => workers.filter(w => w.referrer_id === parentId);

  const RenderNode = ({ node, depth = 0 }: { node: any, depth?: number }) => {
    const children = getChildren(node.id);
    return (
      <div className="flex flex-col">
        <div 
          className="flex items-center p-3 mb-2 bg-white border border-gray-200 rounded-lg shadow-sm"
          style={{ marginLeft: `${depth * 2}rem` }}
        >
          <User className="w-5 h-5 text-indigo-500 mr-3" />
          <div className="flex-1">
            <div className="font-medium text-gray-900">Работник #{node.id}</div>
            <div className="text-xs text-gray-500">Кандидат #{node.candidate_id} | Партнер #{node.partner_id || 'Нет'}</div>
          </div>
          <div className="text-sm font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">
            Привел: {children.length}
          </div>
        </div>
        {children.map(child => (
          <RenderNode key={child.id} node={child} depth={depth + 1} />
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
            <Users className="w-6 h-6 mr-2 text-indigo-600" />
            Реферальная структура
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Кто кого пригласил. Доступно только Владельцу.
          </p>
        </div>
      </div>

      <div className="bg-gray-50 p-6 rounded-xl border border-gray-200 min-h-[500px]">
        {roots.length === 0 ? (
          <div className="text-center text-gray-500 mt-10">Нет данных о работниках</div>
        ) : (
          roots.map(root => (
            <RenderNode key={root.id} node={root} />
          ))
        )}
      </div>
    </div>
  );
}
