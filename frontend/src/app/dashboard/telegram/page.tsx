'use client';

import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Search, Send, Menu, ArrowLeft, Loader2, Info } from 'lucide-react';

export default function TelegramPage() {
  const { user } = useAuth();
  const [chats, setChats] = useState<any[]>([]);
  const [activeChat, setActiveChat] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputText, setInputText] = useState('');
  
  const [loadingChats, setLoadingChats] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchChats = async () => {
    try {
      const { data } = await api.get('/telegram/proxy/chats');
      setChats(data);
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('К вам не привязан активный рабочий Telegram аккаунт. Обратитесь к Owner.');
      } else {
        setError(err.response?.data?.detail || 'Ошибка загрузки чатов');
      }
    } finally {
      setLoadingChats(false);
    }
  };

  const fetchMessages = async (chatId: string) => {
    try {
      const { data } = await api.get(`/telegram/proxy/messages/${chatId}`);
      // Reverse because Telegram returns newest first
      setMessages(data.reverse());
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingMessages(false);
    }
  };

  useEffect(() => {
    fetchChats();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (activeChat) {
      setLoadingMessages(true);
      fetchMessages(activeChat.id);
      
      // Simple polling for live updates
      interval = setInterval(() => {
        fetchMessages(activeChat.id);
      }, 5000);
    }
    return () => clearInterval(interval);
  }, [activeChat]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || !activeChat) return;
    
    const text = inputText;
    setInputText('');
    
    // Optimistic UI update
    setMessages(prev => [...prev, { id: 'temp', text, out: true, date: new Date().toISOString() }]);
    
    try {
      await api.post('/telegram/proxy/send', { chat_id: activeChat.id, text });
      fetchMessages(activeChat.id);
    } catch (err) {
      alert('Ошибка при отправке сообщения');
    }
  };

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh]">
        <div className="bg-red-50 text-red-600 p-6 rounded-xl flex flex-col items-center gap-4 text-center max-w-md">
          <Info className="w-12 h-12" />
          <p className="font-medium text-lg">{error}</p>
          <p className="text-sm opacity-80">Политика безопасности не позволяет использовать аккаунт, если он не привязан к вам в CRM.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-80px)] -m-4 sm:-m-8 bg-white flex border-t border-gray-200 overflow-hidden shadow-sm">
      {/* Sidebar (Chat list) */}
      <div className={`w-full sm:w-[350px] border-r border-gray-200 flex flex-col ${activeChat ? 'hidden sm:flex' : 'flex'}`}>
        {/* Header */}
        <div className="p-3 flex items-center gap-4 border-b border-gray-100 bg-gray-50/50">
          <Menu className="w-6 h-6 text-gray-500 cursor-pointer hover:text-gray-800" />
          <div className="relative flex-1">
            <input 
              type="text" 
              placeholder="Поиск..." 
              className="w-full bg-gray-100 rounded-full py-1.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2" />
          </div>
        </div>
        
        {/* Chat List */}
        <div className="flex-1 overflow-y-auto">
          {loadingChats ? (
            <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
          ) : (
            chats.map(chat => (
              <div 
                key={chat.id} 
                onClick={() => setActiveChat(chat)}
                className={`flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 transition ${activeChat?.id === chat.id ? 'bg-indigo-50/50' : ''}`}
              >
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex-shrink-0 flex items-center justify-center text-white font-medium">
                  {chat.name ? chat.name.charAt(0).toUpperCase() : '?'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline mb-1">
                    <h3 className="font-medium text-gray-900 truncate">{chat.name}</h3>
                    {chat.date && <span className="text-xs text-gray-500">{new Date(chat.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>}
                  </div>
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-500 truncate">{chat.message}</p>
                    {chat.unread_count > 0 && (
                      <span className="bg-indigo-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full ml-2">
                        {chat.unread_count}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className={`flex-1 flex flex-col bg-[#F4F4F5] ${!activeChat ? 'hidden sm:flex' : 'flex'}`}>
        {activeChat ? (
          <>
            {/* Chat Header */}
            <div className="h-14 px-4 bg-white border-b border-gray-200 flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <button className="sm:hidden p-1 -ml-1 text-gray-500" onClick={() => setActiveChat(null)}>
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-medium">
                  {activeChat.name ? activeChat.name.charAt(0).toUpperCase() : '?'}
                </div>
                <div>
                  <h2 className="font-semibold text-gray-900 leading-tight">{activeChat.name}</h2>
                  <p className="text-xs text-gray-500">Был(а) недавно</p>
                </div>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ backgroundImage: "url('https://web.telegram.org/a/chat-bg-pattern-light.png')", backgroundSize: '400px', opacity: 0.95 }}>
              {loadingMessages && messages.length === 0 ? (
                <div className="flex justify-center p-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
              ) : (
                messages.map((msg: any) => (
                  <div key={msg.id} className={`flex ${msg.out ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[75%] sm:max-w-[60%] rounded-2xl px-4 py-2 shadow-sm ${msg.out ? 'bg-[#EEFFDE] rounded-br-none text-gray-900' : 'bg-white rounded-bl-none text-gray-900'}`}>
                      <p className="text-[15px] whitespace-pre-wrap break-words leading-relaxed">{msg.text}</p>
                      <div className="flex justify-end items-center gap-1 mt-1">
                        <span className="text-[11px] text-gray-400/80">{msg.date ? new Date(msg.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : ''}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-3 bg-white border-t border-gray-200 shrink-0">
              <form onSubmit={handleSend} className="max-w-4xl mx-auto flex items-end gap-2 relative">
                <textarea 
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(e); } }}
                  placeholder="Написать сообщение..."
                  className="flex-1 max-h-32 min-h-[44px] bg-gray-100 rounded-xl px-4 py-3 resize-none focus:outline-none focus:bg-white focus:ring-2 focus:ring-indigo-500/50 text-[15px] leading-relaxed transition"
                  rows={1}
                />
                <button 
                  type="submit" 
                  disabled={!inputText.trim()}
                  className="w-11 h-11 rounded-full bg-indigo-500 flex items-center justify-center text-white hover:bg-indigo-600 disabled:opacity-50 disabled:bg-gray-300 transition shrink-0"
                >
                  <Send className="w-5 h-5 ml-0.5" />
                </button>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50/50">
            <span className="bg-gray-200/50 text-gray-500 px-4 py-1.5 rounded-full text-sm font-medium">Выберите чат...</span>
          </div>
        )}
      </div>
    </div>
  );
}
