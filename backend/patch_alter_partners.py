with open("backend/app/main.py", "r") as f:
    content = f.read()

import re

alter_code = """
@app.on_event("startup")
def auto_migrate():
    from app.db.database import engine, Base
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS country VARCHAR;"))
            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS seats INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS payment_terms VARCHAR;"))
            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS experience VARCHAR;"))
            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS registration_time VARCHAR;"))
            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS response_time VARCHAR;"))
            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS rating FLOAT;"))
            conn.execute(text("ALTER TABLE partners ADD COLUMN IF NOT EXISTS last_contact_date VARCHAR;"))
            conn.commit()
    except Exception as e:
        print("Migration error:", e)
"""

content = re.sub(r'@app\.on_event\("startup"\)[\s\S]*?Base\.metadata\.create_all\(bind=engine\)', alter_code.strip(), content)

with open("backend/app/main.py", "w") as f:
    f.write(content)
