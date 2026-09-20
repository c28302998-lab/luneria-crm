with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "r") as f:
    content = f.read()

import re

old_td = """                <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                  <select
                    className="border border-gray-300 rounded-md text-sm p-1"
                    value={acc.assigned_user_id || ''}
                    onChange={(e) => handleAssign(acc.id, e.target.value)}
                  >
                    <option value="">Не назначен</option>
                    {users.filter(u => u.role !== 'CANDIDATE').map(u => (
                      <option key={u.id} value={u.id}>{u.name} (Роль: {u.role})</option>
                    ))}
                  </select>
                </td>"""

new_td = """                <td className="px-6 py-4 whitespace-nowrap space-y-2">
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

if old_td in content:
    content = content.replace(old_td, new_td)
else:
    print("WARNING: Could not find old_td")

with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "w") as f:
    f.write(content)
