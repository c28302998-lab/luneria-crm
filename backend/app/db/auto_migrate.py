from sqlalchemy import text
from app.db.database import engine

def auto_upgrade_schema():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE telegram_accounts ADD COLUMN assigned_worker_id INTEGER;"))
        except Exception:
            pass
            
        try:
            conn.execute(text("ALTER TABLE telegram_accounts ADD COLUMN responsible_admin_id INTEGER;"))
        except Exception:
            pass
            
        try:
            conn.execute(text("ALTER TABLE email_accounts ADD COLUMN responsible_admin_id INTEGER;"))
        except Exception:
            pass

    # Create missing tables (Task, Shift, AccountReview, AccountAssignment, InviteToken, etc)
    from app.models.models import Base
    from app.models import telegram, email
    Base.metadata.create_all(bind=engine)
    print("Auto-migration complete.")
