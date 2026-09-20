with open("src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

state_add = """
  const [fineAmount, setFineAmount] = useState('');
  const [fineReason, setFineReason] = useState('');
  const [fineType, setFineType] = useState('FINE');
  const [fineProofUrl, setFineProofUrl] = useState('');
  const [showFineModal, setShowFineModal] = useState(false);
"""
content = content.replace("const [generatedCreds, setGeneratedCreds] = useState<{email: string, password?: string, message: string} | null>(null);", "const [generatedCreds, setGeneratedCreds] = useState<{email: string, password?: string, message: string} | null>(null);\n" + state_add)

submit_add = """
  const handleSubmitFine = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/balance-requests/', {
        worker_id: parseInt(id as string),
        type: fineType,
        amount: parseFloat(fineAmount),
        reason: fineReason,
        proof_url: fineProofUrl || null
      });
      alert('Заявка отправлена Овнеру на проверку');
      setShowFineModal(false);
      setFineAmount('');
      setFineReason('');
      setFineProofUrl('');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    }
  };
"""
content = content.replace("const fetchData = async () => {", submit_add + "\n  const fetchData = async () => {")

button_add = """            {user?.role === 'ADMIN' && (
              <button onClick={() => setShowFineModal(true)} className="ml-4 text-xs bg-white text-purple-700 px-4 py-2 rounded-full font-bold shadow-sm hover:bg-pink-50 transition-colors">
                Выписать Штраф / Премию
              </button>
            )}"""
content = content.replace("</div>\n          <div className=\"bg-white/10 p-6 flex flex-col justify-center items-center relative overflow-hidden\">", button_add + "\n          </div>\n          <div className=\"bg-white/10 p-6 flex flex-col justify-center items-center relative overflow-hidden\">")

modal_add = """      {showFineModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-xl font-bold text-foreground mb-4">Заявка на Штраф / Премию</h3>
            <form onSubmit={handleSubmitFine} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Тип</label>
                <select value={fineType} onChange={e => setFineType(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground">
                  <option value="FINE">Штраф</option>
                  <option value="BONUS">Премия</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Сумма ($)</label>
                <input type="number" required min="0.01" step="0.01" value={fineAmount} onChange={e => setFineAmount(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" placeholder="Например: 50" />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Причина</label>
                <textarea required value={fineReason} onChange={e => setFineReason(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" rows={3} placeholder="Подробно опишите причину..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Ссылка на доказательство (Скриншот)</label>
                <input type="url" value={fineProofUrl} onChange={e => setFineProofUrl(e.target.value)} className="w-full border-border rounded-lg bg-card text-foreground" placeholder="https://..." />
                <p className="text-xs text-muted-foreground mt-1">Загрузите скриншот на любой хостинг (например, imgur) и вставьте ссылку</p>
              </div>
              <div className="flex justify-end space-x-3 pt-4 border-t border-border mt-6">
                <button type="button" onClick={() => setShowFineModal(false)} className="px-4 py-2 text-muted-foreground hover:bg-muted rounded-lg transition-colors">Отмена</button>
                <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors">Отправить заявку</button>
              </div>
            </form>
          </div>
        </div>
      )}"""

content = content.replace("</div>\n  );\n}", modal_add + "\n    </div>\n  );\n}")

with open("src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
