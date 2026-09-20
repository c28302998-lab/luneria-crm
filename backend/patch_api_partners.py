with open("backend/app/api/partners.py", "r") as f:
    content = f.read()

import re

if "sync_partner_to_sheets" not in content:
    content = content.replace("from app.crud.audit import log_audit", "from app.crud.audit import log_audit\nfrom app.services.google_sheets import sync_partner_to_sheets\nfrom fastapi import BackgroundTasks")

old_create = """def create_partner(partner_in: PartnerCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    partner = Partner(**partner_in.dict())
    db.add(partner)
    db.commit()
    db.refresh(partner)
    log_audit(db, current_user.id, "CREATE", "Partner", partner.id, partner_in.dict())
    return partner"""

new_create = """def create_partner(partner_in: PartnerCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    partner = Partner(**partner_in.dict())
    db.add(partner)
    db.commit()
    db.refresh(partner)
    log_audit(db, current_user.id, "CREATE", "Partner", partner.id, partner_in.dict())
    
    background_tasks.add_task(
        sync_partner_to_sheets,
        partner.id, partner.company_name, partner.contact, partner.country, 
        partner.seats, partner.payment_terms, partner.experience, 
        partner.registration_time, partner.response_time, partner.rating, partner.last_contact_date
    )
    
    return partner"""

old_update = """def update_partner(partner_id: int, partner_in: PartnerCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    partner = db.query(Partner).filter(Partner.is_deleted == False).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
        
    for key, value in partner_in.dict(exclude_unset=True).items():
        setattr(partner, key, value)
        
    db.commit()
    db.refresh(partner)
    log_audit(db, current_user.id, "UPDATE", "Partner", partner.id, partner_in.dict())
    return partner"""

new_update = """def update_partner(partner_id: int, partner_in: PartnerCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    partner = db.query(Partner).filter(Partner.is_deleted == False).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
        
    for key, value in partner_in.dict(exclude_unset=True).items():
        setattr(partner, key, value)
        
    db.commit()
    db.refresh(partner)
    log_audit(db, current_user.id, "UPDATE", "Partner", partner.id, partner_in.dict())
    
    background_tasks.add_task(
        sync_partner_to_sheets,
        partner.id, partner.company_name, partner.contact, partner.country, 
        partner.seats, partner.payment_terms, partner.experience, 
        partner.registration_time, partner.response_time, partner.rating, partner.last_contact_date
    )
    
    return partner"""

content = content.replace(old_create, new_create).replace(old_update, new_update)

with open("backend/app/api/partners.py", "w") as f:
    f.write(content)
