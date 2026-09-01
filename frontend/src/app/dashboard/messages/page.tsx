'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Send, User, ChevronLeft } from 'lucide-react';

export default function MessagesPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  
  const [activeChatUserId, setActiveChatUserId] = useState<number | null>(null);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    const fetchUsersAndMessages = async () => {
      try {
        const [usersRes, msgsRes] = await Promise.all([
          api.get('/users/'),
          api.get('/messages/')
        ]);
        
        // Filter out self and apply chat visibility rules
        let visibleUsers = usersRes.data.filter((u: any) => u.id !== user?.id);
        
        if (user?.role !== 'OWNER') {
          // If the logged-in user is not the OWNER, they can ONLY chat with the OWNER
          visibleUsers = visibleUsers.filter((u: any) => u.role === 'OWNER');
        }
        
        setUsers(visibleUsers);
        
        setMessages(msgsRes.data.reverse()); // Reverse because API sends desc (newest first), we want bottom-up
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingUsers(false);
      }
    };
    if (user) fetchUsersAndMessages();
  }, [user]);

  const refreshMessages = async () => {
    try {
      const { data } = await api.get('/messages/');
      setMessages(data.reverse());
    } catch (err) {}
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeChatUserId) return;
    try {
      await api.post('/messages/', {
        receiver_id: activeChatUserId,
        content: newMessage
      });
      setNewMessage('');
      refreshMessages();
    } catch (err) {
      console.error(err);
    }
  };

  const activeChatMessages = messages.filter(
    m => (m.sender_id === user?.id && m.receiver_id === activeChatUserId) ||
         (m.sender_id === activeChatUserId && m.receiver_id === user?.id)
  );

  return (
    <div className="flex h-[calc(100vh-8rem)] bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className={`${activeChatUserId ? 'hidden md:flex' : 'flex'} w-full md:w-1/3 border-r border-gray-200 bg-gray-50 flex-col`}>
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-medium text-gray-900">Коллеги</h3>
        </div>
        <div className="overflow-y-auto flex-1 p-2 space-y-1">
          {loadingUsers ? <p className="p-4 text-sm text-gray-500">Загрузка...</p> : users.map(u => {
            const unreadCount = messages.filter(m => m.sender_id === u.id && m.receiver_id === user?.id && !m.is_read).length;
            return (
              <div 
                key={u.id} 
                onClick={async () => {
                  setActiveChatUserId(u.id);
                  if (unreadCount > 0) {
                    try {
                      await api.patch(`/messages/mark-read/${u.id}`);
                      refreshMessages();
                    } catch (err) {}
                  }
                }}
                className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition ${
                  activeChatUserId === u.id ? 'bg-indigo-50 border border-indigo-100' : 'hover:bg-gray-100 border border-transparent'
                }`}
              >
                <div className="flex items-center">
                  <div className="bg-gray-200 rounded-full p-2 mr-3">
                    <User className="w-5 h-5 text-gray-500" />
                  </div>
                  <div>
                    <p className={`text-sm font-medium ${activeChatUserId === u.id ? 'text-indigo-900' : 'text-gray-900'}`}>{u.name}</p>
                    <p className="text-xs text-gray-500">{u.role}</p>
                  </div>
                </div>
                {unreadCount > 0 && (
                  <div className="bg-indigo-600 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {unreadCount}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
      
      <div className={`${activeChatUserId ? 'flex' : 'hidden md:flex'} flex-1 flex-col bg-white`}>
        {!activeChatUserId ? (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            Выберите чат слева, чтобы начать общение
          </div>
        ) : (
          <>
            <div className="p-4 border-b border-gray-200 flex items-center shadow-sm z-10">
              <button 
                onClick={() => setActiveChatUserId(null)}
                className="md:hidden mr-3 p-1.5 bg-gray-100 rounded-full text-gray-600 hover:bg-gray-200 focus:outline-none"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <h3 className="font-medium text-gray-900">
                {users.find(u => u.id === activeChatUserId)?.name}
              </h3>
            </div>
            
            <div className="flex-1 p-6 overflow-y-auto space-y-4">
              {activeChatMessages.length === 0 ? (
                <p className="text-gray-400 text-center text-sm mt-10">Нет сообщений. Напишите первым!</p>
              ) : (
                activeChatMessages.map((msg: any) => (
                  <div key={msg.id} className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-md px-4 py-2 rounded-2xl ${
                      msg.sender_id === user?.id 
                        ? 'bg-indigo-600 text-white rounded-br-none' 
                        : 'bg-gray-100 text-gray-900 rounded-bl-none'
                    }`}>
                      <p className="text-sm">{msg.content}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
            
            <div className="p-4 border-t border-gray-200 bg-gray-50">
              <form onSubmit={handleSend} className="flex space-x-2">
                <input 
                  type="text" 
                  value={newMessage}
                  onChange={e => setNewMessage(e.target.value)}
                  placeholder="Введите сообщение..." 
                  className="flex-1 border border-gray-300 rounded-full px-5 py-2 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <button 
                  type="submit" 
                  disabled={!newMessage.trim()}
                  className="p-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <Send className="w-5 h-5 ml-1 mr-1" />
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
