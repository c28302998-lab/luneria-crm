with open('backend/app/main.py', 'r') as f:
    content = f.read()

old_list = '        "ALTER TABLE telegram_accounts ADD COLUMN mask_client_names BOOLEAN DEFAULT FALSE;"\n    ]'
new_list = '''        "ALTER TABLE telegram_accounts ADD COLUMN mask_client_names BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE telegram_accounts ADD COLUMN assigned_worker_id INTEGER;",
        "ALTER TABLE telegram_accounts ADD COLUMN responsible_admin_id INTEGER;",
        "ALTER TABLE email_accounts ADD COLUMN responsible_admin_id INTEGER;"
    ]'''

content = content.replace(old_list, new_list)

with open('backend/app/main.py', 'w') as f:
    f.write(content)
