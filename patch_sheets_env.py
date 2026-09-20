with open('backend/app/services/google_sheets.py', 'r') as f:
    content = f.read()

# I need to change:
#        # 1. Update Main Accounts Sheet
#        # If partner_name is provided, use that worksheet instead of sheet1
#        if partner_name:
#            try:
#                sheet = client.open_by_key(sheet_id).worksheet(partner_name)
#            except gspread.exceptions.WorksheetNotFound:
#                sheet = client.open_by_key(sheet_id).add_worksheet(title=partner_name, rows="1000", cols="20")
#                sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата назначения", "Дата выхода"], 1)

content = content.replace(
'''        # 1. Update Main Accounts Sheet
        # If partner_name is provided, use that worksheet instead of sheet1
        if partner_name:
            try:
                sheet = client.open_by_key(sheet_id).worksheet(partner_name)
            except gspread.exceptions.WorksheetNotFound:
                sheet = client.open_by_key(sheet_id).add_worksheet(title=partner_name, rows="1000", cols="20")
                sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата назначения", "Дата выхода"], 1)''',
'''        # 1. Update Main Accounts Sheet
        
        # Check if this CRM instance has a custom tab name configured in Render Env Vars
        import os
        custom_tab_name = os.environ.get("GOOGLE_SHEET_TAB_NAME")
        
        target_tab_name = partner_name or custom_tab_name
        
        if target_tab_name:
            try:
                sheet = client.open_by_key(sheet_id).worksheet(target_tab_name)
            except gspread.exceptions.WorksheetNotFound:
                sheet = client.open_by_key(sheet_id).add_worksheet(title=target_tab_name, rows="1000", cols="20")
                sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата назначения", "Дата выхода"], 1)'''
)

with open('backend/app/services/google_sheets.py', 'w') as f:
    f.write(content)
