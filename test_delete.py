from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_fpc3bD6JvIkQ@ep-summer-sun-b1e2s4lf-pooler.c-5.eu-central-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

from app.models.models import User
from app.crud.audit import log_audit

try:
    user_id = 7
    user = db.query(User).filter(User.is_deleted == False).filter(User.id == user_id).first()
    if not user:
        print("User not found")
    else:
        print(f"Found user: {user.email}")
        user.is_deleted = True
        user.deleted_at = datetime.datetime.utcnow()
        user.status = "INACTIVE"
        user.email = f"{user.email}_deleted_{user.id}_{int(datetime.datetime.utcnow().timestamp())}"
        
        log_audit(db, 1, "DELETE", "User", user.id, {"is_deleted": True})
        db.commit()
        print("Deleted successfully!")
except Exception as e:
    print(f"Exception: {e}")

