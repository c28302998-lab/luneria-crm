'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { 
  Sparkles, CheckCircle2, DollarSign, Globe, ShieldCheck, X, 
  Monitor, Clock, Heart, HelpCircle, ArrowRight, UserCheck, BookOpen, Repeat, Moon
} from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [success, setSuccess] = useState(false);
  
  const [formData, setFormData] = useState({
    first_name: '',
    age: '',
    experience: '',
    english_level: '',
    desired_income: '',
    is_studying: false,
    is_longterm: false,
    telegram: '', email: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/candidates/apply', {
        ...formData,
        age: parseInt(formData.age),
        source: 'Landing Page'
      });
      setSuccess(true);
      setTimeout(() => {
        setIsModalOpen(false);
        setSuccess(false);
        setFormData({
          first_name: '', age: '', experience: '', english_level: '', desired_income: '', is_studying: false, is_longterm: false, telegram: '', email: ''
        });
      }, 3000);
    } catch (err) {
      alert("Ошибка при отправке заявки. Попробуйте еще раз.");
    }
  };

  return (
    <div className="min-h-screen bg-[#FDF8FA] text-slate-800 font-sans selection:bg-pink-300">
      {/* Header */}
      <header className="fixed w-full top-0 z-40 bg-white/80 backdrop-blur-md border-b border-pink-100">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center"><Moon className="w-6 h-6 text-pink-500" /></div>
            <span className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-purple-600">{process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery"}</span>
          </div>
          <div className="flex gap-4">
            <Link href="/login" className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-pink-600 transition-colors">Войти</Link>
            <button onClick={() => setIsModalOpen(true)} className="px-5 py-2 text-sm font-semibold rounded-full bg-pink-500 text-white shadow-lg shadow-pink-500/30 hover:bg-pink-600 hover:scale-105 transition-all">
              Оставить заявку
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-[500px] bg-pink-300/20 blur-[120px] rounded-full pointer-events-none"></div>
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-pink-100 text-pink-700 text-sm font-semibold mb-6">
            <Sparkles className="w-4 h-4" /> Топ рекрут-агентство в OF индустрии
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 text-slate-900 leading-tight">
            Лучшие условия работы в <br/>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00AFF0] to-pink-500">OnlyFans</span> индустрии
          </h1>
          <p className="text-lg text-slate-600 mb-10 max-w-2xl mx-auto">
            Мы не просто агентство с моделями — мы рекрут-агентство, которое помогает найти идеальные условия. 
            Покрываем недоплаты, выдаем бонусы из своего кошелька и знаем, где ты заработаешь больше всего.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button onClick={() => setIsModalOpen(true)} className="px-8 py-4 w-full sm:w-auto text-lg font-bold rounded-full bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-xl shadow-pink-500/30 hover:shadow-2xl hover:scale-105 transition-all">
              Начать зарабатывать
            </button>
            <a href="#advantages" className="px-8 py-4 w-full sm:w-auto text-lg font-bold rounded-full bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 transition-all">
              Узнать больше
            </a>
          </div>
        </div>
      </section>

      {/* Advantages */}
      <section id="advantages" className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-16 text-slate-900">Почему выбирают {process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery"}?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-3xl bg-pink-50 border border-pink-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-pink-100 rounded-xl flex items-center justify-center text-pink-600 mb-4">
                <DollarSign className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-2">Защита от недоплат и бонусы</h3>
              <p className="text-slate-600">Мы сами покрываем недоплаты со стороны других агентств и регулярно начисляем бонусы из собственного бюджета.</p>
            </div>
            <div className="p-6 rounded-3xl bg-blue-50 border border-blue-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-[#00AFF0] mb-4">
                <Globe className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-2">Мониторинг рынка</h3>
              <p className="text-slate-600">Мы держим руку на пульсе индустрии и всегда знаем, где, с кем и когда вы сможете заработать максимум.</p>
            </div>
            <div className="p-6 rounded-3xl bg-purple-50 border border-purple-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-purple-600 mb-4">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-2">Надежность и кураторство</h3>
              <p className="text-slate-600">За каждым сотрудником закрепляется личный куратор для поддержки 24/7. Мы защищаем ваши интересы на всех этапах.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Numbers / Guarantees */}
      <section className="py-20 bg-gradient-to-br from-pink-500 to-purple-600 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-white opacity-10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
        <div className="max-w-6xl mx-auto px-4 relative z-10 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-10">Твои доходы под нашей защитой</h2>
          <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8 md:p-12 border border-white/20 max-w-4xl mx-auto">
            <h3 className="text-2xl font-semibold mb-4">Средний заработок новичка: <span className="font-extrabold text-4xl">$400 - $1000</span></h3>
            <p className="text-lg text-pink-100">
              Если в первый месяц ты заработаешь меньше минимума, <strong className="text-white">мы компенсируем недостающую сумму прямо из своего кармана!</strong>
            </p>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-20 bg-[#FDF8FA]">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-16 text-slate-900">Как мы работаем?</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50 relative">
              <div className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 font-bold flex items-center justify-center absolute -top-4 -left-4 border-4 border-[#FDF8FA]">1</div>
              <h4 className="text-lg font-bold mb-2 flex items-center gap-2"><Heart className="w-5 h-5 text-pink-500"/> Оставляешь заявку</h4>
              <p className="text-slate-600 text-sm">Заполняешь короткую анкету на сайте, это займет всего пару минут.</p>
            </div>
            
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50 relative">
              <div className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 font-bold flex items-center justify-center absolute -top-4 -left-4 border-4 border-[#FDF8FA]">2</div>
              <h4 className="text-lg font-bold mb-2 flex items-center gap-2"><HelpCircle className="w-5 h-5 text-pink-500"/> С тобой связываются</h4>
              <p className="text-slate-600 text-sm">Наш менеджер пишет тебе в Telegram для уточнения деталей.</p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50 relative">
              <div className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 font-bold flex items-center justify-center absolute -top-4 -left-4 border-4 border-[#FDF8FA]">3</div>
              <h4 className="text-lg font-bold mb-2 flex items-center gap-2"><UserCheck className="w-5 h-5 text-pink-500"/> Трудоустройство</h4>
              <p className="text-slate-600 text-sm">Подбираем лучшее место работы под твои навыки и устраиваем тебя.</p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50 relative">
              <div className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 font-bold flex items-center justify-center absolute -top-4 -left-4 border-4 border-[#FDF8FA]">4</div>
              <h4 className="text-lg font-bold mb-2 flex items-center gap-2"><BookOpen className="w-5 h-5 text-pink-500"/> Обучение</h4>
              <p className="text-slate-600 text-sm">Получаешь все необходимые знания от личного куратора.</p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50 relative">
              <div className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 font-bold flex items-center justify-center absolute -top-4 -left-4 border-4 border-[#FDF8FA]">5</div>
              <h4 className="text-lg font-bold mb-2 flex items-center gap-2"><DollarSign className="w-5 h-5 text-pink-500"/> Выход на смену</h4>
              <p className="text-slate-600 text-sm">Выходишь в первую смену и начинаешь зарабатывать реальные деньги.</p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50 relative">
              <div className="w-8 h-8 rounded-full bg-pink-100 text-pink-600 font-bold flex items-center justify-center absolute -top-4 -left-4 border-4 border-[#FDF8FA]">6</div>
              <h4 className="text-lg font-bold mb-2 flex items-center gap-2"><Repeat className="w-5 h-5 text-pink-500"/> Рост и перевод</h4>
              <p className="text-slate-600 text-sm">Если находим более выгодные условия на рынке — пересаживаем на лучший вариант!</p>
            </div>
          </div>
        </div>
      </section>

      {/* Requirements Section */}
      <section className="py-20 bg-white border-y border-pink-100">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-10 text-slate-900">Кого мы ждем в команду?</h2>
          <div className="flex flex-col md:flex-row gap-6 justify-center">
            <div className="flex-1 bg-slate-50 rounded-2xl p-6 border border-slate-100 flex flex-col items-center">
              <CheckCircle2 className="w-10 h-10 text-green-500 mb-4" />
              <h4 className="font-bold text-lg mb-2">Берем без опыта</h4>
              <p className="text-sm text-slate-600">Мы всему научим. Главное — желание работать и развиваться.</p>
            </div>
            <div className="flex-1 bg-slate-50 rounded-2xl p-6 border border-slate-100 flex flex-col items-center">
              <Monitor className="w-10 h-10 text-blue-500 mb-4" />
              <h4 className="font-bold text-lg mb-2">Наличие ПК обязательно</h4>
              <p className="text-sm text-slate-600">Для комфортной работы необходим компьютер или ноутбук.</p>
            </div>
            <div className="flex-1 bg-slate-50 rounded-2xl p-6 border border-slate-100 flex flex-col items-center">
              <Clock className="w-10 h-10 text-orange-500 mb-4" />
              <h4 className="font-bold text-lg mb-2">Смена 8 часов</h4>
              <p className="text-sm text-slate-600">Полноценный рабочий день для достижения максимального результата.</p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-[#FDF8FA]">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-10 text-slate-900">Частые вопросы</h2>
          <div className="space-y-4">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50">
              <h4 className="font-bold text-lg mb-2 text-slate-900">А это безопасно / анонимно? Требуется ли верификация по документам?</h4>
              <p className="text-slate-600">Да, это полностью безопасно и анонимно. Никакая верификация по вашим личным документам не требуется.</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50">
              <h4 className="font-bold text-lg mb-2 text-slate-900">Как часто происходят выплаты?</h4>
              <p className="text-slate-600">График выплат зависит от условий конкретного проекта, который мы для вас подберем. Но мы всегда предоставляем авансы нашим сотрудникам!</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-pink-50">
              <h4 className="font-bold text-lg mb-2 text-slate-900">Можно ли совмещать работу с учебой?</h4>
              <p className="text-slate-600">Можно, но для достижения максимального результата мы рекомендуем фокусироваться на работе (приоритет отдаем тем кандидатам, кто не учится).</p>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="py-24 bg-white text-center">
        <h2 className="text-4xl font-bold text-slate-900 mb-6">Готов начать зарабатывать?</h2>
        <p className="text-lg text-slate-600 mb-8">Оставь заявку сейчас, и мы подберем для тебя лучшие условия.</p>
        <button onClick={() => setIsModalOpen(true)} className="px-10 py-5 text-xl font-bold rounded-full bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-xl shadow-pink-500/30 hover:shadow-2xl hover:scale-105 transition-all">
          Оставить заявку
        </button>
      </section>

      {/* Footer */}
      <footer className="py-10 bg-slate-900 text-slate-400 text-center">
        <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center"><Moon className="w-5 h-5 text-pink-500" /></div>
            <span className="font-bold text-lg text-white">{process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery Agency"}</span>
        </div>
        <p>© 2026 {process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery"}. All rights reserved.</p>
      </footer>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden relative animate-in fade-in zoom-in duration-200 overflow-y-auto max-h-[90vh]">
            <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors z-10">
              <X className="w-5 h-5" />
            </button>
            
            <div className="p-8">
              {success ? (
                <div className="text-center py-10">
                  <div className="w-16 h-16 bg-green-100 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <h3 className="text-2xl font-bold text-slate-900 mb-2">Заявка отправлена!</h3>
                  <p className="text-slate-600">Мы свяжемся с вами в Telegram в ближайшее время.</p>
                </div>
              ) : (
                <>
                  <h3 className="text-2xl font-bold text-slate-900 mb-6">Оставить заявку</h3>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Ваше имя</label>
                      <input type="text" required value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:outline-none" placeholder="Алиса" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1">Возраст</label>
                        <input type="number" required value={formData.age} onChange={e => setFormData({...formData, age: e.target.value})} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:outline-none" placeholder="18+" />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1">Английский</label>
                        <select required value={formData.english_level} onChange={e => setFormData({...formData, english_level: e.target.value})} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:outline-none">
                          <option value="">Выберите</option>
                          <option value="A1-A2">Базовый</option>
                          <option value="B1-B2">Средний</option>
                          <option value="C1-C2">Свободный</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Опыт работы (в OF/чатах)</label>
                      <input type="text" value={formData.experience} onChange={e => setFormData({...formData, experience: e.target.value})} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:outline-none" placeholder="Без опыта / 6 месяцев" />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Желаемый заработок (1й месяц)</label>
                      <input type="text" value={formData.desired_income} onChange={e => setFormData({...formData, desired_income: e.target.value})} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:outline-none" placeholder="$500 - $1000" />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Ваш Telegram (username)</label>
                      <input type="text" required value={formData.telegram} onChange={e => setFormData({...formData, telegram: e.target.value})} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:outline-none" placeholder="@username" />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Email (для входа в кабинет)</label>
                      <input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:outline-none" placeholder="work@example.com" />
                    </div>
                    
                    <div className="flex items-center gap-3 mt-4">
                      <input type="checkbox" id="study" checked={formData.is_studying} onChange={e => setFormData({...formData, is_studying: e.target.checked})} className="w-5 h-5 text-pink-500 rounded border-slate-300 focus:ring-pink-500" />
                      <label htmlFor="study" className="text-sm text-slate-700">Я сейчас учусь/работаю</label>
                    </div>
                    <div className="flex items-center gap-3">
                      <input type="checkbox" id="longterm" checked={formData.is_longterm} onChange={e => setFormData({...formData, is_longterm: e.target.checked})} className="w-5 h-5 text-pink-500 rounded border-slate-300 focus:ring-pink-500" />
                      <label htmlFor="longterm" className="text-sm text-slate-700">Рассматриваю долгосрочную работу</label>
                    </div>

                    <button type="submit" className="w-full py-4 mt-6 text-lg font-bold rounded-xl bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg shadow-pink-500/30 hover:shadow-xl hover:scale-[1.02] transition-all">
                      Отправить заявку
                    </button>
                  </form>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
