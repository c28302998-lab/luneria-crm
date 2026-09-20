with open('backend/app/services/google_sheets.py', 'r') as f:
    content = f.read()

content = content.replace(
'''def sync_account_to_sheets(
    account_id: int, 
    account_name: str, 
    phone: str, 
    password: str, 
    worker_name: str, 
    admin_name: str, 
    start_date: str,
    action: str = "UPDATE",
    partner_name: str = None
):''',
'''def sync_account_to_sheets(
    account_id: int, 
    account_name: str, 
    phone: str, 
    password: str, 
    worker_name: str, 
    admin_name: str, 
    start_date: str,
    action: str = "UPDATE",
    partner_name: str = None,
    email_address: str = ""
):'''
)

content = content.replace(
'''sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата назначения", "Дата выхода"], 1)''',
'''sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата назначения", "Дата выхода", "Почта"], 1)'''
)

content = content.replace(
'''            row_data = [
                str(account_id),
                account_name or "",
                phone or "",
                password or "",
                worker_name or "Свободен",
                admin_name or "Без админа",
                start_date or ""
            ]
            if cell:
                sheet.update(f"A{cell.row}:G{cell.row}", [row_data])
            else:
                sheet.append_row(row_data)''',
'''            row_data = [
                str(account_id),
                account_name or "",
                phone or "",
                password or "",
                worker_name or "Свободен",
                admin_name or "Без админа",
                start_date or "",
                "", # Дата выхода (leave empty on create/update)
                email_address or ""
            ]
            if cell:
                sheet.update(f"A{cell.row}:I{cell.row}", [row_data])
            else:
                sheet.append_row(row_data)'''
)

with open('backend/app/services/google_sheets.py', 'w') as f:
    f.write(content)
