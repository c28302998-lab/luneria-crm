with open("frontend/src/app/dashboard/my-accounts/page.tsx", "r") as f:
    content = f.read()

import re

old_password = """                  <div>
                    <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Пароль 2FA</span>
                    <div className="bg-white px-3 py-2 border border-slate-200 rounded font-mono text-sm mt-1">
                      {acc.two_fa_password || '—'}
                    </div>
                  </div>"""

new_username = """                  {acc.username && (
                    <div>
                      <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Username</span>
                      <p className="font-medium text-slate-900">@{acc.username.replace('@', '')}</p>
                    </div>
                  )}"""

content = content.replace(old_password, new_username)

with open("frontend/src/app/dashboard/my-accounts/page.tsx", "w") as f:
    f.write(content)
