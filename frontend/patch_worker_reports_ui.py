with open("src/app/dashboard/worker-reports/page.tsx", "r") as f:
    content = f.read()

# Add Notes column header
content = content.replace(
    '<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">ID Работника</th>',
    '<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">ID Работника</th>\n                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Ник/Имя</th>'
)

# Add Notes cell and Fix Files rendering
old_row = """                    <td className="px-6 py-4 text-sm text-foreground">User #{r.worker_id}</td>
                    <td className="px-6 py-4 text-sm font-bold text-green-500">${r.amount}</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">{r.files.length} шт.</td>"""

new_row = """                    <td className="px-6 py-4 text-sm text-foreground">User #{r.worker_id}</td>
                    <td className="px-6 py-4 text-sm text-foreground">{r.notes || '-'}</td>
                    <td className="px-6 py-4 text-sm font-bold text-green-500">${r.amount}</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">
                      {r.files && r.files.length > 0 ? (
                        <a href={r.files[0]} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">
                          Скриншот
                        </a>
                      ) : (
                        "Нет"
                      )}
                    </td>"""

content = content.replace(old_row, new_row)

with open("src/app/dashboard/worker-reports/page.tsx", "w") as f:
    f.write(content)
