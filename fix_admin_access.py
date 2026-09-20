with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "if (user?.role === 'OWNER') {",
    "if (user?.role === 'OWNER' || user?.role === 'ADMIN') {"
)

content = content.replace(
    "if (user?.role !== 'OWNER') return <div>Access Denied</div>;",
    "if (user?.role !== 'OWNER' && user?.role !== 'ADMIN') return <div>Access Denied</div>;"
)

with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "w") as f:
    f.write(content)
