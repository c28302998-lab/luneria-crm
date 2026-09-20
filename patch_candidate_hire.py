with open('frontend/src/app/dashboard/candidates/[id]/page.tsx', 'r') as f:
    content = f.read()

import re

old_func = """  const handleConvertToWorker = async () => {
    if (!confirm('Вы уверены, что хотите перевести этого кандидата в Работники? Он появится в разделе "Работники".')) return;
    try {
      await api.post('/workers/', { candidate_id: candidate.id });
      alert('Кандидат успешно переведен в работники!');
      router.push('/dashboard/workers');
    } catch (err) {
      console.error(err);
      alert('Ошибка при переводе в работники');
    }
  };"""

new_func = """  const handleConvertToWorker = async () => {
    if (!confirm('Вы уверены, что хотите перевести этого кандидата в Работники? Он появится в разделе "Работники".')) return;
    try {
      const { data } = await api.post('/workers/', { candidate_id: candidate.id });
      if (data.invite_link) {
         prompt('Кандидат успешно переведен в работники! Скопируйте ссылку-приглашение и отправьте работнику для установки пароля:', window.location.origin + data.invite_link);
      } else {
         alert('Кандидат успешно переведен в работники!');
      }
      router.push('/dashboard/workers');
    } catch (err) {
      console.error(err);
      alert('Ошибка при переводе в работники');
    }
  };"""

content = content.replace(old_func, new_func)

with open('frontend/src/app/dashboard/candidates/[id]/page.tsx', 'w') as f:
    f.write(content)
