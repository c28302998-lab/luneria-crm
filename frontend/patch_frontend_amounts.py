import re

with open("src/app/dashboard/worker-reports/page.tsx", "r") as f:
    content = f.read()

# Replace action column rendering for APPROVED statuses
old_td = """                    <td className="px-6 py-4 text-right">
                      {r.status === 'PENDING' && (user?.role === 'OWNER' || user?.role === 'FINANCE') && ("""

new_td = """                    <td className="px-6 py-4 text-right">
                      {r.status === 'APPROVED' && (
                        <div className="flex flex-col items-end gap-1 text-xs text-muted-foreground">
                          <div>Работнику: <span className="font-medium text-green-600">${r.worker_amount || 0}</span></div>
                          <div>Админу {r.admin_name ? `(${r.admin_name})` : ''}: <span className="font-medium text-blue-600">${r.admin_amount || 0}</span></div>
                        </div>
                      )}
                      {r.status === 'PENDING' && (user?.role === 'OWNER' || user?.role === 'FINANCE') && ("""

content = content.replace(old_td, new_td)

with open("src/app/dashboard/worker-reports/page.tsx", "w") as f:
    f.write(content)
