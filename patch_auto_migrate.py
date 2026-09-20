import re

with open("backend/app/main.py", "r") as f:
    content = f.read()

new_func = """@app.on_event("startup")
def auto_migrate():
    from app.db.database import engine, Base
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
    
    migrations = [
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS country VARCHAR;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS seats INTEGER DEFAULT 0;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS payment_terms VARCHAR;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS experience VARCHAR;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS registration_time VARCHAR;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS response_time VARCHAR;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS rating FLOAT;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS last_contact_date VARCHAR;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS advances VARCHAR;",
        "ALTER TABLE partners ADD COLUMN IF NOT EXISTS schedules VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS raw_password VARCHAR;",
        "ALTER TABLE telegram_accounts ADD COLUMN IF NOT EXISTS worker_note TEXT;",
        "ALTER TABLE telegram_accounts ADD COLUMN IF NOT EXISTS mask_client_names BOOLEAN DEFAULT FALSE;"
    ]
    
    with engine.connect() as conn:
        for query in migrations:
            try:
                conn.execute(text(query))
                conn.commit()
            except Exception as e:
                pass"""

content = re.sub(
    r'@app\.on_event\("startup"\)\s*def auto_migrate\(\):.*?conn\.commit\(\)\s*except Exception as e:\s*print\("Migration error:", e\)',
    new_func,
    content,
    flags=re.DOTALL
)

with open("backend/app/main.py", "w") as f:
    f.write(content)
