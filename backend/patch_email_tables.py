from app.db.database import engine
from app.models.email import EmailAccount, EmailRequest, EmailAuditLog

print("Creating tables...")
EmailAccount.__table__.create(engine, checkfirst=True)
EmailRequest.__table__.create(engine, checkfirst=True)
EmailAuditLog.__table__.create(engine, checkfirst=True)
print("Done.")
