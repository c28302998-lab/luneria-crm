with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'r') as f:
    content = f.read()

import re

old_func = """  const handleCreateAccount = async () => {
    try {
      const { data } = await api.post(`/workers/${id}/create-account`);
      alert(`Аккаунт успешно создан!\n\nEmail: ${data.email}\nПароль: ${data.password}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при создании аккаунта');
    }
  };"""

new_func = """  const handleCreateAccount = async () => {
    try {
      const { data } = await api.post(`/workers/${id}/create-account`);
      prompt(`Аккаунт успешно создан! Скопируйте ссылку и передайте воркеру для установки пароля:`, window.location.origin + data.invite_link);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при создании аккаунта');
    }
  };"""

content = content.replace(old_func, new_func)

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'w') as f:
    f.write(content)
