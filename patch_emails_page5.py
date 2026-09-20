import re

with open('frontend/src/app/dashboard/emails/page.tsx', 'r') as f:
    content = f.read()

# 1. Fetch admins
if 'const [admins, setAdmins] = useState<any[]>([]);' not in content:
    content = content.replace(
        'const [workers, setWorkers] = useState<any[]>([]);',
        'const [workers, setWorkers] = useState<any[]>([]);\n  const [admins, setAdmins] = useState<any[]>([]);'
    )
    
    content = content.replace(
        'setWorkers(data.filter((u: any) => u.role === \'WORKER\'));',
        'setWorkers(data.filter((u: any) => u.role === \'WORKER\'));\n      setAdmins(data.filter((u: any) => u.role === \'ADMIN\'));'
    )

# 2. Add Delete function
if 'const handleDelete =' not in content:
    content = content.replace(
        'const handleAdd = async (e: React.FormEvent) => {',
        '''const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот аккаунт?')) return;
    try {
      await api.delete(`/emails/accounts/${id}`);
      fetchAccounts();
    } catch (e: any) {
      alert("Ошибка удаления");
    }
  };

  const handleAssign = async (id: number, field: string, val: any) => {
    try {
      await api.patch(`/emails/accounts/${id}`, { [field]: val || null });
      fetchAccounts();
    } catch (e: any) {
      alert("Ошибка назначения");
    }
  };

  const handleAdd = async (e: React.FormEvent) => {'''
    )

# 3. Add Admin Select to Form
if 'assigned_admin_id: e.target.value' not in content:
    content = content.replace(
        '<button type="submit"',
        '''<div>
              <label className="block text-sm font-medium mb-1">Назначить админу</label>
              <select value={(formData as any).assigned_admin_id || ''} onChange={e => setFormData({...formData, assigned_admin_id: e.target.value ? parseInt(e.target.value) : undefined})} className="w-full p-2 rounded border bg-background">
                <option value="">Не назначено</option>
                {admins.map(a => (
                  <option key={a.id} value={a.id}>{a.first_name} {a.last_name} ({a.email})</option>
                ))}
              </select>
            </div>
            <button type="submit"'''
    )

# 4. Redesign Card to show dropdowns and delete button
card_html = '''<div className="flex justify-between items-start">
                <h3 className="font-medium text-lg truncate">{acc.email_address}</h3>
                {(user?.role === 'OWNER' || user?.role === 'ADMIN') && (
                  <button onClick={() => handleDelete(acc.id)} className="text-red-500 hover:text-red-700 text-sm">Удалить</button>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Статус: <span className={acc.status === 'ACTIVE' ? 'text-green-500' : 'text-red-500'}>{acc.status}</span>
              </p>
              
              {(user?.role === 'OWNER' || user?.role === 'ADMIN') ? (
                <div className="mt-3 space-y-2">
                  {user?.role === 'OWNER' && (
                    <div className="flex items-center text-sm">
                      <span className="w-20 text-gray-500">Админ:</span>
                      <select 
                        value={acc.assigned_admin_id || ''} 
                        onChange={e => handleAssign(acc.id, 'assigned_admin_id', e.target.value ? parseInt(e.target.value) : null)}
                        className="flex-1 p-1 text-xs border rounded bg-background"
                      >
                        <option value="">Не назначен</option>
                        {admins.map(a => <option key={a.id} value={a.id}>{a.first_name} ({a.email})</option>)}
                      </select>
                    </div>
                  )}
                  <div className="flex items-center text-sm">
                    <span className="w-20 text-gray-500">Работник:</span>
                    <select 
                      value={acc.assigned_worker_id || ''} 
                      onChange={e => handleAssign(acc.id, 'assigned_worker_id', e.target.value ? parseInt(e.target.value) : null)}
                      className="flex-1 p-1 text-xs border rounded bg-background"
                    >
                      <option value="">Не назначен</option>
                      {workers.map(w => <option key={w.id} value={w.id}>{w.first_name} ({w.email})</option>)}
                    </select>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-500 mt-1">Выдано вам</p>
              )}'''

# Replace the old card content. The old card starts after `<div key={acc.id}... flex-col justify-between">`
# and has a `<div>` wrapping the h3 and p.
content = re.sub(
    r'<div>\s*<h3 className="font-medium text-lg truncate">\{acc\.email_address\}</h3>.*?</div>',
    card_html,
    content,
    flags=re.DOTALL
)

with open('frontend/src/app/dashboard/emails/page.tsx', 'w') as f:
    f.write(content)
