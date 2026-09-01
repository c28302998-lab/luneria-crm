'use client';

import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Search, Send, Menu, ArrowLeft, Loader2, Info, Edit2 } from 'lucide-react';

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
  const [showSettings, setShowSettings] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestType, setRequestType] = useState('');
  const [requestReason, setRequestReason] = useState('');
  const [requestSending, setRequestSending] = useState(false);
  
  const handleSettingsAction = (type: string) => {
    setRequestType(type);
    setShowSettings(false);
    setShowRequestModal(true);
  };
  
  
  const handleSetAlias = async (chatId: string) => {
    const alias = prompt(`Внутреннее имя клиента (пусто = сброс):`);
    if (alias === null) return;
    try {
      await api.post(`/telegram/proxy/chats/${chatId}/alias`, { custom_name: alias });
      fetchChats();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка сохранения имени');
    }
  };

  const submitRequest = async () => {
    setRequestSending(true);
    try {
      await api.post('/telegram/proxy/requests', {
        request_type: requestType,
        reason: requestReason
      });
      alert('Запрос успешно отправлен Owner-у.');
      setShowRequestModal(false);
      setRequestReason('');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка отправки запроса');
    } finally {
      setRequestSending(false);
    }
  };


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
                    <div className="relative">
            <Menu 
              onClick={() => setShowSettings(!showSettings)}
              className="w-6 h-6 text-gray-500 cursor-pointer hover:text-gray-800" 
            />
            {showSettings && (
              <div className="absolute top-8 left-0 w-56 bg-white rounded-md shadow-lg border border-gray-100 z-50 py-1">
                <div className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">Настройки аккаунта</div>
                <button onClick={() => handleSettingsAction('CHANGE_PASSWORD')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Изменить пароль</button>
                <button onClick={() => handleSettingsAction('CHANGE_PHONE')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Изменить номер телефона</button>
                <button onClick={() => handleSettingsAction('CHANGE_2FA')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Настройки 2FA</button>
                <button onClick={() => handleSettingsAction('TERMINATE_SESSIONS')} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Завершить другие сеансы</button>
                <button onClick={() => handleSettingsAction('LOGOUT')} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Выйти</button>
              </div>
            )}
          </div>
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
                                    <h2 className="font-semibold text-gray-900 leading-tight flex items-center gap-2">
                    {activeChat.name}
                    {user?.role === 'OWNER' && (
                      <button onClick={() => handleSetAlias(activeChat.id)} className="text-gray-400 hover:text-indigo-600 p-1" title="Задать внутреннее имя">
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </h2>
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
      
      {/* Request Modal */}
      {showRequestModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md overflow-hidden">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Требуется одобрение Owner</h3>
              <p className="text-sm text-gray-500 mb-4">
                Для выполнения этого действия ({requestType}) требуется разрешение Владельца. Опишите причину запроса:
              </p>
              
              <textarea
                value={requestReason}
                onChange={(e) => setRequestReason(e.target.value)}
                className="w-full border border-gray-300 rounded-md p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows={4}
                placeholder="Например: Смена рабочего устройства, забыл облачный пароль..."
              />
            </div>
            
            <div className="px-6 py-4 bg-gray-50 flex justify-end gap-3">
              <button 
                onClick={() => setShowRequestModal(false)}
                className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition"
              >
                Отмена
              </button>
              <button 
                onClick={submitRequest}
                disabled={requestSending || !requestReason.trim()}
                className="px-4 py-2 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-md transition disabled:opacity-50 flex items-center gap-2"
              >
                {requestSending && <Loader2 className="w-4 h-4 animate-spin" />}
                Отправить запрос
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </div>
  );
}
