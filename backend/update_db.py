from app.db.database import engine, Base
import sqlite3

def add_is_read_column():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE messages ADD COLUMN is_read BOOLEAN DEFAULT 0')
        conn.commit()
        print("Column is_read added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error (maybe already exists): {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_is_read_column()
