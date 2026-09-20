import re

with open("frontend/src/app/dashboard/crm-accounts/page.tsx", "r") as f:
    content = f.read()

# Add edit state and function
edit_state = """  const [passwords, setPasswords] = useState<Record<number, string>>({});
  const [editingUser, setEditingUser] = useState<any>(null);
  
  const handleSaveUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    try {
      await api.patch(`/users/${editingUser.id}`, {
        name: editingUser.name,
        email: editingUser.email,
        status: editingUser.status
      });
      setEditingUser(null);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка сохранения');
    }
  };"""

content = content.replace("  const [passwords, setPasswords] = useState<Record<number, string>>({});", edit_state)

# Update Actions Column header
content = content.replace(
    '<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">СТАТУС</th>',
    '<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">СТАТУС</th>\n<th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>'
)

# Update Table Body
actions_cell = """                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button 
                        onClick={() => setEditingUser(u)}
                        className="text-primary hover:underline text-sm font-medium"
                      >
                        Изменить
                      </button>
                    </td>
                  </tr>"""
content = content.replace("                  </tr>", actions_cell)

# Add Modal at the end of the file
modal_html = """        )}
      </div>

      {editingUser && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-background rounded-xl p-6 w-full max-w-md shadow-xl border border-border">
            <h2 className="text-xl font-semibold text-foreground mb-4">Редактировать Аккаунт</h2>
            <form onSubmit={handleSaveUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                <input 
                  type="text" 
                  value={editingUser.name}
                  onChange={e => setEditingUser({...editingUser, name: e.target.value})}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground" 
                  required 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email / Логин</label>
                <input 
                  type="email" 
                  value={editingUser.email}
                  onChange={e => setEditingUser({...editingUser, email: e.target.value})}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground" 
                  required 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Статус</label>
                <select
                  value={editingUser.status}
                  onChange={e => setEditingUser({...editingUser, status: e.target.value})}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground" 
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="BLOCKED">BLOCKED</option>
                  <option value="SUSPENDED">SUSPENDED</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button 
                  type="button" 
                  onClick={() => setEditingUser(null)}
                  className="px-4 py-2 border border-border rounded-lg text-sm text-foreground hover:bg-muted"
                >
                  Отмена
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 shadow"
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
}"""

content = content.replace("        )}\n      </div>\n    </div>\n  );\n}", modal_html)

with open("frontend/src/app/dashboard/crm-accounts/page.tsx", "w") as f:
    f.write(content)
