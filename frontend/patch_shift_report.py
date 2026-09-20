import re

with open("src/app/dashboard/shift-report/page.tsx", "r") as f:
    content = f.read()

# Add state
content = content.replace("const [amount, setAmount] = useState('');", "const [amount, setAmount] = useState('');\n  const [notes, setNotes] = useState('');\n  const [links, setLinks] = useState('');")

# Update POST request
content = content.replace("files: [] // Mocks file upload for now", "files: links ? [links] : [],\n        notes: notes")

# Replace form HTML
old_form = """            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">Скриншоты статистики</label>
              <div className="border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:bg-muted/50 transition-colors">
                <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
                <span className="text-sm text-muted-foreground">Нажмите или перетащите файлы</span>
              </div>
            </div>"""

new_form = """            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">Ник рабочего аккаунта / Ваше имя</label>
              <input 
                type="text" required 
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="block w-full rounded-xl border border-border bg-background p-3 text-foreground focus:ring-2 focus:ring-primary focus:outline-none" 
                placeholder="Например: Qwerty/Алексей"
              />
            </div>
            
            <div className="bg-pink-50 text-pink-800 p-4 rounded-xl text-sm border border-pink-100">
              <strong className="block mb-1">Важно:</strong>
              Продажи считаются ВСЕ, которые вы сделали за день (неважно, ваши 20% или нет). 
              Скидывайте сюда всё, что продали за сегодня.
            </div>

            <div>
              <label className="block text-sm font-semibold text-foreground mb-2">Скриншоты статистики (Ссылка на Imgur/Postimages)</label>
              <input 
                type="url" required 
                value={links}
                onChange={(e) => setLinks(e.target.value)}
                className="block w-full rounded-xl border border-border bg-background p-3 text-foreground focus:ring-2 focus:ring-primary focus:outline-none" 
                placeholder="https://imgur.com/..."
              />
            </div>"""

content = content.replace(old_form, new_form)

with open("src/app/dashboard/shift-report/page.tsx", "w") as f:
    f.write(content)
