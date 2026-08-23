from sqlalchemy.orm import Session
from app.models.models import AuditLog

def log_audit(db: Session, user_id: int, action: str, entity_type: str, entity_id: int, changes: dict):
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes
    )
    db.add(log_entry)
    db.commit()
