from app.db.database import engine, Base
import sqlite3

def run_migrations():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE payments ADD COLUMN amount_company FLOAT DEFAULT 0.0')
        cursor.execute('ALTER TABLE payments ADD COLUMN amount_worker FLOAT DEFAULT 0.0')
        cursor.execute('ALTER TABLE payments ADD COLUMN amount_admin FLOAT DEFAULT 0.0')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reason VARCHAR,
            amount FLOAT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER REFERENCES users(id),
            deleted_at DATETIME
        )
        ''')
        conn.commit()
        print("Finance tables updated.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migrations()
