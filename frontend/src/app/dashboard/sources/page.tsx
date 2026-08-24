'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Plus, Trash2, FileText, Upload, ChevronDown, ChevronUp , Globe} from 'lucide-react';

interface Source {
  id: number;
  title: string;
  content: string;
  files: string[];
  created_at: string;
}

export default function SourcesPage() {
  const { user } = useAuth();
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ title: '', content: '' });
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const fetchSources = async () => {
    try {
      const res = await api.get('/sources/');
      setSources(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/sources/', formData);
      const newSourceId = res.data.id;
      
      for (const file of selectedFiles) {
        const fd = new FormData();
        fd.append('file', file);
        await api.post(`/sources/${newSourceId}/files`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }

      setIsModalOpen(false);
      setFormData({ title: '', content: '' });
      setSelectedFiles([]);
      fetchSources();
    } catch (err) {
      alert('Ошибка при создании источника');
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить материал?')) return;
    try {
      await api.delete(`/sources/${id}`);
      fetchSources();
    } catch (err) {
      alert('Ошибка при удалении');
    }
  };

  const handleFileUpload = async (sourceId: number, file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    try {
      await api.post(`/sources/${sourceId}/files`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchSources();
    } catch (err) {
      alert('Ошибка загрузки файла');
    }
  };

  const canEdit = user?.role === 'OWNER' || user?.role === 'CURATOR';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">Источники и Шаблоны</h2>
        {canEdit && (
          <button 
            onClick={() => { setIsModalOpen(true); setSelectedFiles([]); setFormData({ title: '', content: '' }); }}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
          >
            <Plus className="h-4 w-4 mr-2" />
            Добавить
          </button>
        )}
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-500">Загрузка...</div>
      ) : sources.length === 0 ? (
        <div className="p-8 text-center bg-white rounded-xl shadow-sm border border-gray-200 text-gray-500">
          Источники пока не добавлены
        </div>
      ) : (
        <div className="space-y-4">
          {sources.map(m => (
            <div key={m.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div 
                className="p-4 flex justify-between items-center cursor-pointer hover:bg-gray-50"
                onClick={() => setExpandedId(expandedId === m.id ? null : m.id)}
              >
                <div className="flex items-center space-x-3">
                  <Globe className="text-indigo-500 h-5 w-5" />
                  <h3 className="font-semibold text-gray-900">{m.title}</h3>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-xs text-gray-500">
                    {new Date(m.created_at).toLocaleDateString('ru-RU')}
                  </span>
                  {expandedId === m.id ? <ChevronUp className="h-5 w-5 text-gray-400" /> : <ChevronDown className="h-5 w-5 text-gray-400" />}
                </div>
              </div>
              
              {expandedId === m.id && (
                <div className="p-4 border-t border-gray-100 bg-gray-50">
                  <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap mb-4">
                    {m.content}
                  </div>
                  
                  {m.files && m.files.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Прикрепленные файлы</h4>
                      <div className="flex flex-wrap gap-2">
                        {m.files.map((fileUrl, idx) => (
                          <a 
                            key={idx} 
                            href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${fileUrl}`}
                            target="_blank" rel="noreferrer"
                            className="flex items-center px-3 py-1.5 bg-white border border-gray-200 rounded-md text-xs hover:border-indigo-500 transition"
                          >
                            <FileText className="h-3 w-3 mr-1.5 text-gray-400" />
                            Файл {idx + 1}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  {canEdit && (
                    <div className="mt-6 flex items-center justify-between pt-4 border-t border-gray-200">
                      <div>
                        <label className="flex items-center px-3 py-1.5 border border-indigo-200 text-indigo-700 rounded-md text-xs font-medium cursor-pointer hover:bg-indigo-50">
                          <Upload className="h-3 w-3 mr-1.5" />
                          Прикрепить файл
                          <input 
                            type="file" 
                            className="hidden" 
                            onChange={(e) => {
                              if (e.target.files && e.target.files[0]) {
                                handleFileUpload(m.id, e.target.files[0]);
                              }
                            }}
                          />
                        </label>
                      </div>
                      <button 
                        onClick={() => handleDelete(m.id)}
                        className="flex items-center text-xs text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="h-3 w-3 mr-1" />
                        Удалить источник
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Новый источник/шаблон</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Название (Тема)</label>
                <input 
                  type="text" required 
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                  placeholder="Например: Группы в Варшаве"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Содержание (инструкция)</label>
                <textarea 
                  required rows={10}
                  value={formData.content}
                  onChange={(e) => setFormData({...formData, content: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                  placeholder="Пошаговая инструкция..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Прикрепить файлы</label>
                <input 
                  type="file" 
                  multiple
                  onChange={(e) => setSelectedFiles(Array.from(e.target.files || []))}
                  className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
                {selectedFiles.length > 0 && (
                  <div className="mt-2 text-xs text-gray-500 flex flex-col space-y-1">
                    {selectedFiles.map((f, i) => (
                      <span key={i}>- {f.name}</span>
                    ))}
                  </div>
                )}
              </div>
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Отмена
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-indigo-700"
                >
                  Сохранить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
