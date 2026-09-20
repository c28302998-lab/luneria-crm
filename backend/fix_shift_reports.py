from app.db.database import engine
from sqlalchemy import text

def add_notes_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE shift_reports ADD COLUMN notes VARCHAR;"))
            conn.commit()
            print("Successfully added notes to shift_reports")
        except Exception as e:
            print("Error or already added:", e)

if __name__ == "__main__":
    add_notes_column()
