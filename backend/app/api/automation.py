from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User, Task, AuditLog
from app.models.telegram import TelegramAccount
from app.models.email import EmailAccount
from app.core.dependencies import get_current_user, RoleChecker
from pydantic import BaseModel

router = APIRouter()

class AutomationEvent(BaseModel):
    event_type: str # ERROR_SESSION, RATE_LIMIT, UNEXPECTED_LOGIN
    account_type: str # TELEGRAM, EMAIL
    account_id: int
    message: str

@router.post("/trigger")
def trigger_automation(event: AutomationEvent, db: Session = Depends(get_db)):
    # This could be called by internal services (e.g., telegram client), so we might bypass current_user or use a service token.
    # For now, we'll just allow it to trigger.
    
    admin_id = None
    account_name = f"#{event.account_id}"
    
    if event.account_type == "TELEGRAM":
        acc = db.query(TelegramAccount).filter(TelegramAccount.id == event.account_id).first()
        if acc:
            admin_id = acc.responsible_admin_id or acc.assigned_user_id
            account_name = acc.name or acc.username or account_name
    elif event.account_type == "EMAIL":
        acc = db.query(EmailAccount).filter(EmailAccount.id == event.account_id).first()
        if acc:
            admin_id = acc.responsible_admin_id or acc.assigned_admin_id
            account_name = acc.email_address or account_name

    if not admin_id:
        # Fallback to the first OWNER
        owner = db.query(User).filter(User.role == "OWNER").first()
        if owner:
            admin_id = owner.id
            
    if not admin_id:
        raise HTTPException(status_code=500, detail="No admin or owner available to assign the task to")
        
    task = Task(
        title=f"Автоматизация: {event.event_type} на {event.account_type} {account_name}",
        description=event.message,
        priority="HIGH",
        assigned_user_id=admin_id,
        creator_id=1, # System
        status="NEW"
    )
    db.add(task)
    
    log = AuditLog(
        user_id=1,
        action="AUTOMATION_TRIGGERED",
        details=f"Task created for {admin_id} regarding {event.event_type} on {event.account_type} {event.account_id}"
    )
    db.add(log)
    
    db.commit()
    return {"message": "Automation event processed successfully"}

