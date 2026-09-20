import re

with open("src/app/dashboard/telegram-accounts/page.tsx", "r") as f:
    content = f.read()

# Add RefreshCw to lucide-react imports
content = content.replace(
    "Trash, CheckSquare, Key } from 'lucide-react';",
    "Trash, CheckSquare, Key, RefreshCw } from 'lucide-react';"
)

# Add handleSync function
handle_sync_fn = """  const handleSync = async (id: number) => {
    try {
      await api.post(`/telegram/admin/accounts/${id}/sync`);
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при синхронизации');
    }
  };

  const handleApproveIssue"""
content = content.replace("  const handleApproveIssue", handle_sync_fn)

# Add the button in the UI
old_username = """<div className="text-sm text-muted-foreground">{acc.username || 'Нет username'}</div>"""
new_username = """<div className="text-sm text-muted-foreground flex items-center gap-2">
                    {acc.username || 'Нет username'}
                    <button onClick={() => handleSync(acc.id)} className="text-muted-foreground hover:text-primary transition" title="Синхронизировать имя">
                      <RefreshCw className="w-3 h-3" />
                    </button>
                  </div>"""
content = content.replace(old_username, new_username)

with open("src/app/dashboard/telegram-accounts/page.tsx", "w") as f:
    f.write(content)
