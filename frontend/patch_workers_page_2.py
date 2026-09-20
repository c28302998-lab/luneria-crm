with open("src/app/dashboard/workers/page.tsx", "r") as f:
    content = f.read()

old_cell = """                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                        {adminName || `ID #${w.admin_id}`}
                      </td>
                      {user?.role === 'OWNER' && ("""
new_cell = """                      <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                        {adminName}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-primary">
                        {workerUser ? `$${(workerUser.balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '$0.00'}
                      </td>
                      {user?.role === 'OWNER' && ("""
content = content.replace(old_cell, new_cell)

with open("src/app/dashboard/workers/page.tsx", "w") as f:
    f.write(content)
