with open("frontend/src/app/dashboard/crm-accounts/page.tsx", "r") as f:
    content = f.read()

handle_delete = """
  const handleDeleteUser = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return;
    try {
      await api.delete(`/users/${id}`);
      fetchUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при удалении');
    }
  };
"""

content = content.replace(
    "const handleSaveUser = async (e: React.FormEvent) => {",
    handle_delete + "\n  const handleSaveUser = async (e: React.FormEvent) => {"
)

with open("frontend/src/app/dashboard/crm-accounts/page.tsx", "w") as f:
    f.write(content)
