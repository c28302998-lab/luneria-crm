with open("frontend/src/app/dashboard/partners/page.tsx", "r") as f:
    content = f.read()

import re

old_th = """                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Посл. контакт</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>"""

new_th = """                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Посл. контакт</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Людей</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Действия</th>"""

old_td = """                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.last_contact_date}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">"""

new_td = """                    <td className="px-4 py-3 whitespace-nowrap text-sm text-muted-foreground">{p.last_contact_date}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-foreground font-medium">{p.workers_count}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">"""

content = content.replace(old_th, new_th).replace(old_td, new_td)

with open("frontend/src/app/dashboard/partners/page.tsx", "w") as f:
    f.write(content)
