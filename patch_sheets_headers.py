with open("backend/app/services/google_sheets.py", "r") as f:
    content = f.read()

content = content.replace(
    'sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата выхода (назначения)"], 1)',
    'sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата назначения", "Дата выхода"], 1)'
)

with open("backend/app/services/google_sheets.py", "w") as f:
    f.write(content)
