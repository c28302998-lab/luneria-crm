from app.db.database import SessionLocal
from app.models.models import User
from app.core.security import verify_password
import sys

db = SessionLocal()
email = 'owner@lunery.local'
u = db.query(User).filter(User.email == email).first()
if u:
    print(f"User {email} exists. Status: {u.status}, Role: {u.role}")
    print(f"Password 'password123' verification: {verify_password('password123', u.password_hash)}")
else:
    print(f"User {email} NOT FOUND!")
