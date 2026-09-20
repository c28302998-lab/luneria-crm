with open("src/app/dashboard/reports/page.tsx", "r") as f:
    content = f.read()

import re

# Update state
state_update = """  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    income: '',
    content: '',
    proof_url: ''
  });"""
content = re.sub(r'const \[isModalOpen, setIsModalOpen\] = useState\(false\);\s*const \[formData, setFormData\] = useState\(\{[\s\S]*?\}\);', state_update, content)

# Update post payload
post_update = """      await api.post('/reports/', {
        type: 'DAILY_SUMMARY',
        data: {
          title: formData.title,
          income: formData.income,
          content: formData.content,
          proof_url: formData.proof_url
        }
      });
      setIsModalOpen(false);
      setFormData({ title: '', income: '', content: '', proof_url: '' });"""
content = re.sub(r'await api\.post\(\'/reports/\', \{[\s\S]*?\}\);\s*setIsModalOpen\(false\);\s*setFormData\(\{ title: \'\', content: \'\' \}\);', post_update, content)

# Update modal UI
modal_ui = """            <h3 className="text-xl font-bold text-foreground mb-4">Ежедневный Отчет Администратора</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Название отчета (Например: Сводка за 09.09)</label>
                <input 
                  type="text" required 
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full border-border bg-card rounded-lg p-2 text-sm focus:ring-primary focus:border-primary" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Общая Выручка команды ($)</label>
                <input 
                  type="number" step="0.01" required 
                  value={formData.income}
                  onChange={(e) => setFormData({...formData, income: e.target.value})}
                  className="w-full border-border bg-card rounded-lg p-2 text-sm focus:ring-primary focus:border-primary" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Аналитика / Комментарий</label>
                <textarea 
                  required rows={4}
                  value={formData.content}
                  placeholder="Воркеры отработали отлично, трафик с TikTok идет хорошо. Воркер №3 просел, провел с ним беседу."
                  onChange={(e) => setFormData({...formData, content: e.target.value})}
                  className="w-full border-border bg-card rounded-lg p-2 text-sm focus:ring-primary focus:border-primary" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">Скриншот / Доказательства (Ссылка)</label>
                <input 
                  type="url"
                  placeholder="https://..."
                  value={formData.proof_url}
                  onChange={(e) => setFormData({...formData, proof_url: e.target.value})}
                  className="w-full border-border bg-card rounded-lg p-2 text-sm focus:ring-primary focus:border-primary" 
                />
              </div>"""
content = re.sub(r'<h3 className="text-lg font-medium text-foreground mb-4">Новый отчет</h3>\s*<form onSubmit=\{handleCreate\} className="space-y-4">[\s\S]*?</div>\s*<div className="flex justify-end', modal_ui + '\n              <div className="flex justify-end', content)

# Table update to show proof and income
table_row = """                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-foreground">{r.data?.title || 'Без названия'}</span>
                      {r.data?.income && <span className="text-xs text-green-600 font-bold mt-1">Доход: ${r.data?.income}</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground max-w-xs truncate">
                    {r.data?.content || '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">Админ #{r.admin_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                    {new Date(r.created_at).toLocaleDateString('ru-RU')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-y-2 flex flex-col items-end">
                    {r.data?.proof_url && (
                      <a href={r.data.proof_url} target="_blank" rel="noreferrer" className="text-blue-500 hover:text-blue-700 text-xs flex items-center">
                        <FileText className="w-3 h-3 mr-1" /> Пруфы
                      </a>
                    )}
                    <button onClick={() => handleDownload(r)} className="text-primary hover:text-indigo-900 text-xs flex items-center">
                      <Download className="w-3 h-3 mr-1" /> Скачать
                    </button>
                  </td>"""
content = re.sub(r'<td className="px-6 py-4 whitespace-nowrap">\s*<div className="flex items-center">\s*<FileText className="h-5 w-5 text-gray-400 mr-2" />\s*<span className="text-sm font-medium text-foreground">\{r\.data\?\.title \|\| \'Без названия\'\}</span>\s*</div>\s*</td>\s*<td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">\{r\.type\}</td>\s*<td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">Пользователь #\{r\.admin_id\}</td>\s*<td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">\s*\{new Date\(r\.created_at\)\.toLocaleDateString\(\'ru-RU\'\)\}\s*</td>\s*<td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">\s*<button onClick=\{[^}]+\} className="text-primary hover:text-indigo-900 flex items-center justify-end w-full">\s*<Download className="w-4 h-4 mr-1" />\s*Скачать\s*</button>\s*</td>', table_row, content)

# Table headers update
headers = """              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Отчет</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Аналитика</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Автор</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Дата</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase">Действия</th>
              </tr>"""
content = re.sub(r'<tr>\s*<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Название</th>[\s\S]*?Действия</th>\s*</tr>', headers, content)

with open("src/app/dashboard/reports/page.tsx", "w") as f:
    f.write(content)
