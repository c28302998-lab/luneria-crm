with open("src/app/dashboard/admin-payouts/page.tsx", "r") as f:
    content = f.read()

old_title = "<h2 className=\"text-2xl font-semibold text-foreground\">Выплаты админам</h2>"
new_title = "<h2 className=\"text-2xl font-semibold text-foreground\">{user?.role === 'ADMIN' ? 'Мои выплаты' : 'Выплаты админам'}</h2>"

content = content.replace(old_title, new_title)

with open("src/app/dashboard/admin-payouts/page.tsx", "w") as f:
    f.write(content)
