import re

with open("backend/app/main.py", "r") as f:
    content = f.read()

new_migration = """            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS schedules VARCHAR;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS raw_password VARCHAR;"))"""

content = content.replace('            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS schedules VARCHAR;"))', new_migration)

with open("backend/app/main.py", "w") as f:
    f.write(content)
