with open("src/app/dashboard/crm-accounts/page.tsx", "r") as f:
    content = f.read()

import re

# Table row replacement
old_row = """                    <td className="px-6 py-4 whitespace-nowrap">
                      {passwords[u.id] ? (
                        <span className="font-mono bg-green-100 text-green-800 px-2 py-1 rounded text-sm select-all">
                          {passwords[u.id]}
                        </span>
                      ) : (
                        <button 
                          onClick={() => handleResetPassword(u.id)}
                          className="text-xs bg-muted hover:bg-muted/80 text-foreground px-3 py-1.5 rounded transition-colors"
                        >
                          Показать (Сброс)
                        </button>
                      )}
                    </td>"""

new_row = """                    <td className="px-6 py-4 whitespace-nowrap flex items-center gap-2">
                      <span className="font-mono bg-muted text-foreground px-2 py-1 rounded text-sm select-all">
                        {passwords[u.id] || u.raw_password || '—'}
                      </span>
                      <button 
                        onClick={() => handleResetPassword(u.id)}
                        className="text-xs text-primary hover:text-primary/80 transition-colors border border-primary/20 px-2 py-1 rounded"
                      >
                        Сбросить
                      </button>
                    </td>"""

content = content.replace(old_row, new_row)

with open("src/app/dashboard/crm-accounts/page.tsx", "w") as f:
    f.write(content)
