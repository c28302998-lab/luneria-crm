import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_fpc3bD6JvIkQ@ep-summer-sun-b1e2s4lf-pooler.c-5.eu-central-1.aws.neon.tech/neondb?sslmode=require"
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE telegram_accounts ADD COLUMN assigned_worker_id INTEGER REFERENCES users(id) ON DELETE SET NULL;")
    conn.commit()
    print("Added assigned_worker_id")
except Exception as e:
    print(e)
    conn.rollback()

try:
    cur.execute("ALTER TABLE telegram_accounts ADD COLUMN worker_note TEXT;")
    conn.commit()
    print("Added worker_note")
except Exception as e:
    print(e)
    conn.rollback()

cur.close()
conn.close()
