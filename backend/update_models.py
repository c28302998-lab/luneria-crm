import sqlite3

def update():
    conn = sqlite3.connect('sql_app.db')
    c = conn.cursor()
    # Update candidates table
    try:
        c.execute("ALTER TABLE candidates ADD COLUMN experience TEXT;")
        c.execute("ALTER TABLE candidates ADD COLUMN english_level TEXT;")
        c.execute("ALTER TABLE candidates ADD COLUMN desired_income TEXT;")
        c.execute("ALTER TABLE candidates ADD COLUMN is_studying BOOLEAN;")
        c.execute("ALTER TABLE candidates ADD COLUMN is_longterm BOOLEAN;")
    except Exception as e:
        print("Candidate alter:", e)
        
    # Create shift_reports table
    try:
        c.execute("""
        CREATE TABLE IF NOT EXISTS shift_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER,
            amount REAL,
            files JSON,
            status TEXT DEFAULT 'PENDING',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
    except Exception as e:
        print("Shift reports table:", e)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update()
