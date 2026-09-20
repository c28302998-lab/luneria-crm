with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "{users.filter(u => u.role === 'WORKER').map(u => (\n                        <option key={u.id} value={u.id}>{u.name} (WORKER)</option>",
    "{users.filter(u => u.role === 'WORKER' || u.role === 'CANDIDATE').map(u => (\n                        <option key={u.id} value={u.id}>{u.name} ({u.role === 'CANDIDATE' ? 'Кандидат' : 'Воркер'})</option>"
)

content = content.replace(
    '<div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1">Работник:</div>',
    '<div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1">Работник / Кандидат:</div>'
)

with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "w") as f:
    f.write(content)
