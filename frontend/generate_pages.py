import os

base_dir = "/Users/thf/.gemini/antigravity/scratch/luneria/frontend/src/app/dashboard"

pages = {
    "messages": "Сообщения",
    "curators": "Кураторы",
    "admins": "Администраторы",
    "finance": "Финансы",
    "reports": "Отчеты",
    "analytics": "Аналитика"
}

template = """'use client';

import { useAuth } from '@/store/auth';

export default function {component_name}Page() {{
  const {{ user }} = useAuth();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">{title}</h2>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
        <p>Модуль "{title}" находится в разработке.</p>
        <p className="mt-2 text-sm">Скоро здесь появится полноценный функционал.</p>
      </div>
    </div>
  );
}}
"""

for folder, title in pages.items():
    page_dir = os.path.join(base_dir, folder)
    os.makedirs(page_dir, exist_ok=True)
    component_name = folder.capitalize()
    
    with open(os.path.join(page_dir, "page.tsx"), "w") as f:
        f.write(template.format(component_name=component_name, title=title))

print("Created missing pages!")
