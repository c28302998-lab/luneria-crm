import os

base_dir = "/Users/thf/.gemini/antigravity/scratch/luneria/frontend/src/app/dashboard"

files = {
    "messages/page.tsx": """'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Send } from 'lucide-react';

export default function MessagesPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');

  const fetchMessages = async () => {
    try {
      const { data } = await api.get('/messages/');
      setMessages(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;
    try {
      await api.post('/messages/', {
        receiver_id: 1, // Mock receiver for now
        content: newMessage
      });
      setNewMessage('');
      fetchMessages();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="w-1/3 border-r border-gray-200 bg-gray-50 p-4 overflow-y-auto">
        <h3 className="font-medium text-gray-900 mb-4">Диалоги</h3>
        <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-lg cursor-pointer">
          <p className="font-medium text-indigo-900">Общий чат</p>
          <p className="text-xs text-indigo-700 mt-1">Последнее сообщение...</p>
        </div>
      </div>
      <div className="flex-1 flex flex-col">
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {loading ? (
            <p className="text-gray-500 text-center">Загрузка...</p>
          ) : messages.length === 0 ? (
            <p className="text-gray-500 text-center">Нет сообщений</p>
          ) : (
            messages.map((msg: any) => (
              <div key={msg.id} className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs px-4 py-2 rounded-lg ${msg.sender_id === user?.id ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
                  <p className="text-sm">{msg.content}</p>
                </div>
              </div>
            ))
          )}
        </div>
        <div className="p-4 border-t border-gray-200">
          <form onSubmit={handleSend} className="flex space-x-2">
            <input 
              type="text" 
              value={newMessage}
              onChange={e => setNewMessage(e.target.value)}
              placeholder="Введите сообщение..." 
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500"
            />
            <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
""",

    "curators/page.tsx": """'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';

export default function CuratorsPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const { data } = await api.get('/users/');
        setUsers(data.filter((u: any) => u.role === 'CURATOR'));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">Кураторы</h2>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {loading ? <p className="p-8 text-center text-gray-500">Загрузка...</p> : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Имя</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((u: any) => (
                <tr key={u.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{u.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{u.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap"><span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">{u.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
""",

    "admins/page.tsx": """'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export default function AdminsPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const { data } = await api.get('/users/');
        setUsers(data.filter((u: any) => u.role === 'ADMIN'));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">Администраторы</h2>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {loading ? <p className="p-8 text-center text-gray-500">Загрузка...</p> : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Имя</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Куратор ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((u: any) => (
                <tr key={u.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{u.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{u.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{u.curator_id || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap"><span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">{u.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
""",

    "analytics/page.tsx": """'use client';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">Аналитика</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-64 flex flex-col items-center justify-center text-gray-400">
          <p>График конверсии (Скоро)</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-64 flex flex-col items-center justify-center text-gray-400">
          <p>Рост базы кандидатов (Скоро)</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-64 flex flex-col items-center justify-center text-gray-400">
          <p>Эффективность администраторов (Скоро)</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-64 flex flex-col items-center justify-center text-gray-400">
          <p>Финансовый рост (Скоро)</p>
        </div>
      </div>
    </div>
  );
}
"""
}

for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Generated final pages!")
