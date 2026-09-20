with open('frontend/src/app/dashboard/emails/page.tsx', 'r') as f:
    content = f.read()

import re

# We need to add workers fetch and assignment
if 'const [workers, setWorkers] = useState<any[]>([]);' not in content:
    content = content.replace(
        'const [loading, setLoading] = useState(true);',
        'const [loading, setLoading] = useState(true);\n  const [workers, setWorkers] = useState<any[]>([]);'
    )
    
    # fetch workers
    content = content.replace(
        'fetchAccounts();',
        'fetchAccounts();\n    if (user?.role === "OWNER" || user?.role === "ADMIN") fetchWorkers();'
    )
    
    content = content.replace(
        'const fetchAccounts = async () => {',
        '''const fetchWorkers = async () => {
    try {
      const { data } = await api.get('/workers');
      setWorkers(data);
    } catch (e) {}
  };
  
  const fetchAccounts = async () => {'''
    )
    
    # Add worker select to Add Form
    content = content.replace(
        '<button type="submit" className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">Сохранить и проверить</button>',
        '''<div>
              <label className="block text-sm font-medium mb-1">Назначить работнику</label>
              <select value={(formData as any).assigned_worker_id || ''} onChange={e => setFormData({...formData, assigned_worker_id: e.target.value ? parseInt(e.target.value) : undefined})} className="w-full p-2 rounded border bg-background">
                <option value="">Не назначено</option>
                {workers.map(w => (
                  <option key={w.id} value={w.id}>{w.candidate?.first_name} {w.candidate?.last_name} ({w.candidate?.email})</option>
                ))}
              </select>
            </div>
            <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">Сохранить и проверить</button>'''
    )
    
    with open('frontend/src/app/dashboard/emails/page.tsx', 'w') as f:
        f.write(content)
    print("Patched emails page")
else:
    print("Already patched")
