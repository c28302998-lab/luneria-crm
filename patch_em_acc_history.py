import re

with open('frontend/src/app/dashboard/emails/page.tsx', 'r') as f:
    content = f.read()

# Add states for modal
state_injection = """
  // History Modal State
  const [showHistoryModal, setShowHistoryModal] = useState<number | null>(null);
  const [accountHistory, setAccountHistory] = useState<any[]>([]);
"""
content = content.replace("const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);", "const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);\n" + state_injection)

# Add fetch function
fetch_func = """
  const handleOpenHistory = async (id: number) => {
    setShowHistoryModal(id);
    try {
      const res = await api.get(`/emails/accounts/${id}/history`);
      setAccountHistory(res.data);
    } catch (e) {
      console.error(e);
      alert('Ошибка при загрузке истории');
    }
  };
"""
content = content.replace("const handleDelete = async (id: number) => {", fetch_func + "\n  const handleDelete = async (id: number) => {")

# Add Button to Table
button_html = """
                        <button onClick={() => handleOpenHistory(acc.id)} className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title="История назначений">
                          <Activity className="w-4 h-4" />
                        </button>
"""
if "onClick={() => setDeleteConfirm(acc.id)}" in content:
    content = content.replace("<button onClick={() => setDeleteConfirm(acc.id)}", button_html + "\n                        <button onClick={() => setDeleteConfirm(acc.id)}")

# Add Modal JSX at the end
modal_html = """
      {showHistoryModal !== null && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-foreground">История назначений Email</h3>
              <button onClick={() => setShowHistoryModal(null)} className="text-muted-foreground hover:text-foreground">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>
            
            {accountHistory.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">История пуста</p>
            ) : (
              <div className="space-y-4">
                {accountHistory.map((h, i) => (
                  <div key={i} className="flex flex-col sm:flex-row sm:justify-between p-4 bg-muted rounded-lg border border-border">
                    <div>
                      <p className="font-medium text-foreground">Воркер ID: {h.worker_id || 'Неизвестно'}</p>
                      <p className="text-sm text-muted-foreground mt-1">Причина отвязки: {h.reason || 'Активен'}</p>
                    </div>
                    <div className="mt-2 sm:mt-0 text-left sm:text-right text-sm">
                      <p className="text-foreground">Назначен: {new Date(h.assigned_at).toLocaleString()}</p>
                      <p className="text-muted-foreground">Снят: {h.revoked_at ? new Date(h.revoked_at).toLocaleString() : 'По сей день'}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
"""
content = content.replace("</div>\n  );\n}", modal_html + "\n    </div>\n  );\n}")

with open('frontend/src/app/dashboard/emails/page.tsx', 'w') as f:
    f.write(content)
