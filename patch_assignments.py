import re

with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "r") as f:
    content = f.read()

# Modify handleAssign to take a type (admin/worker)
old_handle_assign = """  const handleAssign = async (accId: number, userId: string) => {
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/assign`, {
        user_id: userId ? parseInt(userId) : null
      });
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Ошибка при назначении');
    }
  };"""

new_handle_assign = """  const handleAssignAdmin = async (accId: number, userId: string, workerId: string | null) => {
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/assign`, {
        user_id: userId ? parseInt(userId) : null,
        worker_id: workerId ? parseInt(workerId) : null
      });
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Ошибка при назначении');
    }
  };

  const handleAssignWorker = async (accId: number, adminId: string | null, workerId: string) => {
    try {
      await api.patch(`/telegram/admin/accounts/${accId}/assign`, {
        user_id: adminId ? parseInt(adminId) : null,
        worker_id: workerId ? parseInt(workerId) : null
      });
      fetchAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Ошибка при назначении');
    }
  };"""

content = content.replace(old_handle_assign, new_handle_assign)

# Replace the single dropdown with two dropdowns
old_dropdown = """                <td className="px-6 py-4 whitespace-nowrap">
                  <select 
                    value={acc.assigned_user_id || ''}
                    onChange={(e) => handleAssign(acc.id, e.target.value)}
                    className="w-full px-2 py-1 text-sm border border-border rounded-lg bg-background text-foreground"
                  >
                    <option value="">Не назначен</option>
                    {users.filter(u => u.role !== 'CANDIDATE').map(u => (
                      <option key={u.id} value={u.id}>{u.name} (Роль: {u.role})</option>
                    ))}
                  </select>
                </td>"""

new_dropdown = """                <td className="px-6 py-4 whitespace-nowrap space-y-2">
                  {(user?.role === 'OWNER' || user?.role === 'FINANCE') && (
                    <div>
                      <div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1">Админ / Владелец:</div>
                      <select 
                        value={acc.assigned_user_id || ''}
                        onChange={(e) => handleAssignAdmin(acc.id, e.target.value, acc.assigned_worker_id?.toString() || null)}
                        className="w-full px-2 py-1 text-sm border border-border rounded-lg bg-background text-foreground"
                      >
                        <option value="">Без админа</option>
                        {users.filter(u => ['ADMIN', 'OWNER', 'FINANCE', 'CURATOR'].includes(u.role)).map(u => (
                          <option key={u.id} value={u.id}>{u.name} ({u.role})</option>
                        ))}
                      </select>
                    </div>
                  )}
                  <div>
                    <div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1">Работник:</div>
                    <select 
                      value={acc.assigned_worker_id || ''}
                      onChange={(e) => handleAssignWorker(acc.id, acc.assigned_user_id?.toString() || null, e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-border rounded-lg bg-background text-foreground"
                    >
                      <option value="">Свободен</option>
                      {users.filter(u => u.role === 'WORKER').map(u => (
                        <option key={u.id} value={u.id}>{u.name} (WORKER)</option>
                      ))}
                    </select>
                  </div>
                </td>"""

content = content.replace(old_dropdown, new_dropdown)

with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "w") as f:
    f.write(content)
