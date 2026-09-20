with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    '<button\n          onClick={() => { setAuthStep(1); setShowAddModal(true); }}',
    "{user?.role === 'OWNER' && (\n        <button\n          onClick={() => { setAuthStep(1); setShowAddModal(true); }}"
)

content = content.replace(
    'Добавить аккаунт\n        </button>',
    'Добавить аккаунт\n        </button>\n        )}'
)

with open("frontend/src/app/dashboard/telegram-accounts/page.tsx", "w") as f:
    f.write(content)
