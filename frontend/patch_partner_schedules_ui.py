with open("frontend/src/app/dashboard/partners/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "  advances: string;",
    "  advances: string;\n  schedules: string;"
)

content = content.replace(
    "advances: ''",
    "advances: '',\n    schedules: ''"
)

content = content.replace(
    "advances: p.advances || ''",
    "advances: p.advances || '',\n      schedules: p.schedules || ''"
)

content = content.replace(
    "last_contact_date: '', advances: ''",
    "last_contact_date: '', advances: '', schedules: ''"
)

# Table header
content = content.replace(
    '<th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Авансы</th>',
    '<th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Авансы</th>\n                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Графики</th>'
)

# Table cell
content = content.replace(
    '<td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.advances}</td>',
    '<td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.advances}</td>\n                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.schedules}</td>'
)

# Form field
form_field = """                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Авансы (Есть ли, когда)</label>
                  <input 
                    type="text" 
                    placeholder="Например: Да, через 2 нед."
                    value={formData.advances}
                    onChange={(e) => setFormData({...formData, advances: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Графики</label>
                  <input 
                    type="text" 
                    placeholder="Например: 2/2, 6/1, Ночные"
                    value={formData.schedules}
                    onChange={(e) => setFormData({...formData, schedules: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>"""

content = content.replace("""                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">Авансы (Есть ли, когда)</label>
                  <input 
                    type="text" 
                    placeholder="Например: Да, через 2 нед."
                    value={formData.advances}
                    onChange={(e) => setFormData({...formData, advances: e.target.value})}
                    className="w-full rounded-md border-border bg-background border p-2 text-sm focus:border-primary focus:outline-none" 
                  />
                </div>""", form_field)

with open("frontend/src/app/dashboard/partners/page.tsx", "w") as f:
    f.write(content)
