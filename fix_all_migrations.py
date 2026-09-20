with open("backend/app/main.py", "r") as f:
    content = f.read()

# Replace the wrong column name for email_accounts
content = content.replace(
    '"ALTER TABLE email_accounts ADD COLUMN responsible_admin_id INTEGER;"',
    '"ALTER TABLE email_accounts ADD COLUMN assigned_admin_id INTEGER;"'
)

# Add is_deleted and deleted_at
new_cols = '''        "ALTER TABLE email_accounts ADD COLUMN assigned_admin_id INTEGER;",
        "ALTER TABLE telegram_accounts ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE telegram_accounts ADD COLUMN deleted_at TIMESTAMP;",
        "ALTER TABLE email_accounts ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE email_accounts ADD COLUMN deleted_at TIMESTAMP;"'''

content = content.replace(
    '"ALTER TABLE email_accounts ADD COLUMN assigned_admin_id INTEGER;"',
    new_cols
)

with open("backend/app/main.py", "w") as f:
    f.write(content)
