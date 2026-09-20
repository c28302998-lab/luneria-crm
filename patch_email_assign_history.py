import re

with open('backend/app/api/emails.py', 'r') as f:
    content = f.read()

if "from app.models.email import" in content:
    content = content.replace("from app.models.email import", "from app.models.email import EmailAccountAssignment,")
else:
    content = content.replace("from app.models.models import", "from app.models.email import EmailAccountAssignment\nfrom app.models.models import")

old_code = """    update_dict = update_data.dict(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(acc, k, v)
        
    db.commit()"""

new_code = """    update_dict = update_data.dict(exclude_unset=True)
    
    # Check if assignment changed
    from datetime import datetime
    old_worker_id = acc.assigned_worker_id
    new_worker_id = update_dict.get('assigned_worker_id', old_worker_id)
    
    if 'assigned_worker_id' in update_dict and old_worker_id != new_worker_id:
        active_assignment = db.query(EmailAccountAssignment).filter(
            EmailAccountAssignment.email_account_id == acc.id,
            EmailAccountAssignment.revoked_at == None
        ).first()
        if active_assignment:
            active_assignment.revoked_at = datetime.utcnow()
            active_assignment.reason = "REASSIGNED"
            
        if new_worker_id is not None:
            new_assignment = EmailAccountAssignment(
                email_account_id=acc.id,
                worker_id=new_worker_id,
                admin_id=update_dict.get('assigned_admin_id', acc.assigned_admin_id),
                assigned_at=datetime.utcnow()
            )
            db.add(new_assignment)
            
    for k, v in update_dict.items():
        setattr(acc, k, v)
        
    db.commit()"""

content = content.replace(old_code, new_code)

with open('backend/app/api/emails.py', 'w') as f:
    f.write(content)
