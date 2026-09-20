'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function EmailClientPage() {
  const params = useParams();
  const router = useRouter();
  const accountId = params.id as string;

  const [messages, setMessages] = useState<any[]>([]);
  const [selectedMsg, setSelectedMsg] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [composing, setComposing] = useState(false);
  const [composeData, setComposeData] = useState({ to: '', subject: '', text: '' });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchInbox();
  }, [accountId]);

  const fetchInbox = async () => {
    try {
      setLoading(true);
      const { data } = await api.get(`/emails/${accountId}/inbox`);
      setMessages(data);
    } catch (e: any) {
      alert(e.response?.data?.detail || "Ошибка загрузки писем");
    } finally {
      setLoading(false);
    }
  };

  const openMessage = async (uid: string) => {
    try {
      const { data } = await api.get(`/emails/${accountId}/message/${uid}`);
      setSelectedMsg(data);
    } catch (e: any) {
      alert("Ошибка загрузки письма");
    }
  };

  const sendEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    try {
      await api.post(`/emails/${accountId}/send`, {
        to_email: composeData.to,
        subject: composeData.subject,
        body_text: composeData.text
      });
      setComposing(false);
      setComposeData({ to: '', subject: '', text: '' });
      alert("Письмо успешно отправлено!");
    } catch (e: any) {
      alert(e.response?.data?.detail || "Ошибка при отправке письма");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] max-w-7xl mx-auto border-x border-border">
      {/* Left sidebar - Message list */}
      <div className="w-1/3 border-r border-border bg-card flex flex-col">
        <div className="p-4 border-b border-border flex justify-between items-center bg-background">
          <Link href="/dashboard/emails" className="text-sm text-gray-500 hover:text-primary">← Назад</Link>
          <div className="space-x-2">
            <button onClick={fetchInbox} className="text-sm text-indigo-600 hover:underline">Обновить</button>
            <button onClick={() => {setComposing(true); setSelectedMsg(null);}} className="px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700">Написать</button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-500">Загрузка писем...</div>
          ) : messages.length === 0 ? (
            <div className="p-4 text-center text-gray-500">Нет входящих писем.</div>
          ) : (
            messages.map(msg => (
              <div 
                key={msg.uid} 
                onClick={() => openMessage(msg.uid)}
                className={`p-4 border-b border-border cursor-pointer hover:bg-muted/50 ${selectedMsg?.uid === msg.uid ? 'bg-muted' : ''}`}
              >
                <div className="flex justify-between items-baseline mb-1">
                  <div className={`text-sm truncate ${msg.is_unseen ? 'font-bold text-foreground' : 'text-gray-600'}`}>{msg.sender}</div>
                  <div className="text-xs text-gray-400 flex-shrink-0 ml-2">{new Date(msg.date).toLocaleDateString()}</div>
                </div>
                <div className={`text-sm truncate ${msg.is_unseen ? 'font-bold' : 'text-gray-500'}`}>{msg.subject || 'Без темы'}</div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Right panel - Message view or Compose */}
      <div className="w-2/3 bg-background flex flex-col">
        {composing ? (
          <div className="flex-1 flex flex-col p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold">Новое письмо</h2>
              <button onClick={() => setComposing(false)} className="text-gray-500 hover:text-gray-800">✕ Закрыть</button>
            </div>
            <form onSubmit={sendEmail} className="flex-1 flex flex-col space-y-4">
              <div>
                <input required type="email" placeholder="Кому (Email)" value={composeData.to} onChange={e => setComposeData({...composeData, to: e.target.value})} className="w-full p-2 border-b border-border bg-transparent outline-none" />
              </div>
              <div>
                <input required type="text" placeholder="Тема письма" value={composeData.subject} onChange={e => setComposeData({...composeData, subject: e.target.value})} className="w-full p-2 border-b border-border bg-transparent outline-none font-medium" />
              </div>
              <div className="flex-1">
                <textarea required placeholder="Текст сообщения..." value={composeData.text} onChange={e => setComposeData({...composeData, text: e.target.value})} className="w-full h-full p-2 border border-border rounded-lg bg-transparent outline-none resize-none" />
              </div>
              <div className="pt-2">
                <button type="submit" disabled={sending} className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
                  {sending ? 'Отправка...' : 'Отправить'}
                </button>
              </div>
            </form>
          </div>
        ) : selectedMsg ? (
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            <div className="p-6 border-b border-border">
              <h2 className="text-2xl font-bold mb-4">{selectedMsg.subject || 'Без темы'}</h2>
              <div className="flex justify-between items-center text-sm">
                <div><span className="text-gray-500">От: </span><span className="font-medium">{selectedMsg.sender}</span></div>
                <div className="text-gray-500">{new Date(selectedMsg.date).toLocaleString()}</div>
              </div>
              <div className="mt-4">
                <button onClick={() => {
                  setComposing(true);
                  setComposeData({ to: selectedMsg.sender, subject: `Re: ${selectedMsg.subject}`, text: '' });
                }} className="text-sm px-3 py-1 border border-border rounded hover:bg-muted">Ответить</button>
              </div>
            </div>
            <div className="p-6 flex-1 overflow-y-auto">
              {selectedMsg.html ? (
                <iframe 
                  srcDoc={selectedMsg.html} 
                  className="w-full min-h-[500px] border-0" 
                  sandbox="allow-same-origin allow-popups"
                />
              ) : (
                <div className="whitespace-pre-wrap font-sans text-sm">{selectedMsg.text}</div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            Выберите письмо для просмотра
          </div>
        )}
      </div>
    </div>
  );
}
