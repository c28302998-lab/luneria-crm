with open("src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

import re

# Add state for credentials
imports_fix = """import { ArrowLeft, UserCircle, DollarSign, Clock, Shield, Briefcase, Activity, Key } from 'lucide-react';"""
content = re.sub(r"import \{ ArrowLeft.*\} from 'lucide-react';", imports_fix, content)

state_add = """  const [admin, setAdmin] = useState<any>(null);
  const [generatedCreds, setGeneratedCreds] = useState<{email: string, password?: string, message: string} | null>(null);

  const handleCreateAccount = async () => {
    try {
      const { data } = await api.post(`/workers/${id}/create-account`);
      setGeneratedCreds(data);
      fetchData(); // refresh
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка создания аккаунта');
    }
  };"""
content = content.replace("  const [admin, setAdmin] = useState<any>(null);", state_add)

btn_add = """            {userAccount ? (
              <p className="text-xs text-pink-200 mt-4">ID Аккаунта: {userAccount.id}</p>
            ) : (
              <div className="mt-4 flex flex-col items-center">
                <p className="text-xs text-yellow-200 mb-2">Системный аккаунт еще не создан</p>
                <button onClick={handleCreateAccount} className="text-xs bg-white text-purple-700 px-3 py-1.5 rounded-full font-bold shadow-sm hover:bg-pink-50 transition-colors flex items-center">
                  <Key className="w-3 h-3 mr-1" /> Выдать доступ в CRM
                </button>
              </div>
            )}
            
            {generatedCreds && (
              <div className="absolute inset-0 bg-purple-900/95 backdrop-blur-sm z-20 flex flex-col items-center justify-center p-6 text-left">
                <h4 className="text-white font-bold mb-2 text-center">{generatedCreds.message}</h4>
                {generatedCreds.password && (
                  <div className="w-full bg-black/30 rounded p-3 text-sm space-y-1">
                    <p><span className="text-purple-300">Логин:</span> {generatedCreds.email}</p>
                    <p><span className="text-purple-300">Пароль:</span> <span className="font-mono bg-white/10 px-1 rounded">{generatedCreds.password}</span></p>
                  </div>
                )}
                <p className="text-xs text-purple-200 mt-2 text-center">Скопируйте и передайте работнику.</p>
                <button onClick={() => setGeneratedCreds(null)} className="mt-4 px-4 py-1.5 bg-white/20 hover:bg-white/30 rounded-full text-xs font-bold transition-colors">Закрыть</button>
              </div>
            )}
          </div>
        </div>"""
content = re.sub(r'\{userAccount \? \([\s\S]*?<\/div>\n        <\/div>', btn_add, content)

with open("src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
