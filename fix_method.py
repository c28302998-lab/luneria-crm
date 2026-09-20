with open("frontend/src/app/dashboard/crm-accounts/page.tsx", "r") as f:
    content = f.read()

content = content.replace("await api.patch(`/users/${editingUser.id}`", "await api.put(`/users/${editingUser.id}`")

with open("frontend/src/app/dashboard/crm-accounts/page.tsx", "w") as f:
    f.write(content)
