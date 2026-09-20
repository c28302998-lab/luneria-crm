with open("src/app/dashboard/workers/page.tsx", "r") as f:
    content = f.read()

import re

# Change usersMap to store the whole user
content = content.replace("const [usersMap, setUsersMap] = useState<Record<number, string>>({});", "const [usersMap, setUsersMap] = useState<Record<number, any>>({});")

# Change how usersMap is populated
old_populate = """        const uMap: Record<number, string> = {};
        uData.data.forEach((u: any) => {
          uMap[u.id] = u.name;
        });
        setUsersMap(uMap);"""
new_populate = """        const uMap: Record<number, any> = {};
        uData.data.forEach((u: any) => {
          uMap[u.id] = u;
        });
        setUsersMap(uMap);"""
content = content.replace(old_populate, new_populate)

# Change header
old_header = """                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Админ</th>
                  {user?.role === 'OWNER' && ("""
new_header = """                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Админ</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Баланс</th>
                  {user?.role === 'OWNER' && ("""
content = content.replace(old_header, new_header)

# Change body
old_body = """                  const adminName = usersMap[w.admin_id];
                  return ("""
new_body = """                  const adminUser = usersMap[w.admin_id];
                  const adminName = adminUser ? adminUser.name : `ID: ${w.admin_id}`;
                  const workerUser = candidate ? Object.values(usersMap).find(u => u.email === candidate.email) : null;
                  return ("""
content = content.replace(old_body, new_body)

old_cell = """                      <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                        {adminName || `ID: ${w.admin_id}`}
                      </td>
                      {user?.role === 'OWNER' && ("""
new_cell = """                      <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                        {adminName}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-primary">
                        {workerUser ? `$${(workerUser.balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '—'}
                      </td>
                      {user?.role === 'OWNER' && ("""
content = content.replace(old_cell, new_cell)

with open("src/app/dashboard/workers/page.tsx", "w") as f:
    f.write(content)
