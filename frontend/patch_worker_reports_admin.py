import re

with open("src/app/dashboard/worker-reports/page.tsx", "r") as f:
    content = f.read()

# Replace description text
old_desc = "Здесь вы проверяете и утверждаете отчеты о заработке от ваших работников. После подтверждения баланс автоматически начисляется работнику и вам."
new_desc = "{user?.role === 'ADMIN' ? 'Здесь вы можете отслеживать отчеты ваших работников для удобного сбора ежедневной статистики по команде.' : 'Здесь вы проверяете и утверждаете отчеты о заработке от ваших работников. После подтверждения баланс автоматически начисляется.'}"
content = content.replace(old_desc, new_desc)

# Add stats for admin
old_table_start = '<div className="bg-card shadow-sm rounded-xl border border-border overflow-hidden">'
new_table_start = """      {user?.role === 'ADMIN' && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gradient-to-br from-pink-500 to-purple-600 rounded-xl p-6 text-white shadow-md">
            <h3 className="text-sm font-semibold opacity-90 mb-1">Заработано командой (Сегодня)</h3>
            <div className="text-3xl font-bold">${reports.filter(r => new Date(r.created_at).toDateString() === new Date().toDateString()).reduce((sum, r) => sum + r.amount, 0).toFixed(2)}</div>
          </div>
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-muted-foreground mb-1">Сдано отчетов (Сегодня)</h3>
            <div className="text-3xl font-bold text-foreground">{reports.filter(r => new Date(r.created_at).toDateString() === new Date().toDateString()).length}</div>
          </div>
        </div>
      )}
      <div className="bg-card shadow-sm rounded-xl border border-border overflow-hidden">"""
content = content.replace(old_table_start, new_table_start)

# Replace actions logic
old_actions = """{r.status === 'PENDING' && (
                        <div className="flex flex-col gap-2 items-end">"""

new_actions = """{r.status === 'PENDING' && (user?.role === 'OWNER' || user?.role === 'FINANCE') && (
                        <div className="flex flex-col gap-2 items-end">"""

content = content.replace(old_actions, new_actions)

old_approve_end = """</button>
                        </div>
                      )}
                    </td>"""

new_approve_end = """</button>
                        </div>
                      )}
                      {r.status === 'PENDING' && user?.role === 'ADMIN' && (
                        <span className="text-xs text-muted-foreground italic">Ожидает Овнера</span>
                      )}
                    </td>"""

content = content.replace(old_approve_end, new_approve_end)

with open("src/app/dashboard/worker-reports/page.tsx", "w") as f:
    f.write(content)
