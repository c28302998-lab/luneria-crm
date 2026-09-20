with open("frontend/src/app/dashboard/partners/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "  last_contact_date: string;",
    "  last_contact_date: string;\n  advances: string;"
)

content = content.replace(
    "last_contact_date: ''",
    "last_contact_date: '',\n    advances: ''"
)

content = content.replace(
    "last_contact_date: p.last_contact_date || ''",
    "last_contact_date: p.last_contact_date || '',\n      advances: p.advances || ''"
)

content = content.replace(
    "rating: 0, last_contact_date: ''",
    "rating: 0, last_contact_date: '', advances: ''"
)

# Table header
content = content.replace(
    '<th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Посл. контакт</th>',
    '<th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Посл. контакт</th>\n                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Авансы</th>'
)

# Table cell
content = content.replace(
    '<td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.last_contact_date}</td>',
    '<td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.last_contact_date}</td>\n                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.advances}</td>'
)

# Form field
form_field = """                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Последний контакт</label>
                  <input 
                    type="text" 
                    placeholder="Например: 11.09"
                    value={formData.last_contact_date}
                    onChange={(e) => setFormData({...formData, last_contact_date: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Авансы (Есть ли, когда)</label>
                  <input 
                    type="text" 
                    placeholder="Например: Да, через 2 нед."
                    value={formData.advances}
                    onChange={(e) => setFormData({...formData, advances: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>"""

content = content.replace("""                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Последний контакт</label>
                  <input 
                    type="text" 
                    placeholder="Например: 11.09"
                    value={formData.last_contact_date}
                    onChange={(e) => setFormData({...formData, last_contact_date: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>""", form_field)

with open("frontend/src/app/dashboard/partners/page.tsx", "w") as f:
    f.write(content)
