import re

with open("src/app/dashboard/layout.tsx", "r") as f:
    content = f.read()

old_logo = """<div className="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center mr-3"><Moon className="w-6 h-6 text-pink-500" /></div>
          <span className="text-xl font-bold text-slate-900 tracking-wide">Lunery CRM</span>"""

new_logo = """<div className="w-10 h-10 rounded-full flex items-center justify-center mr-3 overflow-hidden bg-transparent">
            <img src="/logo.png" alt="Lunery Logo" className="w-full h-full object-cover" />
          </div>
          <span className="text-xl font-bold text-slate-900 tracking-wide">Lunery CRM</span>"""

content = content.replace(old_logo, new_logo)

with open("src/app/dashboard/layout.tsx", "w") as f:
    f.write(content)
