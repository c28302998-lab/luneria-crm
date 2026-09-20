with open("src/app/dashboard/worker-reports/page.tsx", "r") as f:
    content = f.read()

content = content.replace("<span>Админу: $</span>", "<span>Админу {r.admin_name ? `(${r.admin_name})` : ''}: $</span>")

with open("src/app/dashboard/worker-reports/page.tsx", "w") as f:
    f.write(content)
