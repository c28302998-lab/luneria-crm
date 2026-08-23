from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Partner
from app.schemas.schemas import Partner as PartnerSchema, PartnerCreate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[PartnerSchema])
def read_partners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    partners = db.query(Partner).filter(Partner.is_deleted == False).offset(skip).limit(limit).all()
    for p in partners:
        p.workers_count = len([w for w in p.workers if not w.is_deleted])
        if current_user.role == "ADMIN":
            p.contact = "***HIDDEN***"
    return partners

@router.post("/", response_model=PartnerSchema)
def create_partner(partner_in: PartnerCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    partner = Partner(**partner_in.dict())
    db.add(partner)
    db.commit()
    db.refresh(partner)
    log_audit(db, current_user.id, "CREATE", "Partner", partner.id, partner_in.dict())
    return partner

@router.put("/{partner_id}", response_model=PartnerSchema)
def update_partner(partner_id: int, partner_in: PartnerCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    partner = db.query(Partner).filter(Partner.is_deleted == False).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
        
    for key, value in partner_in.dict(exclude_unset=True).items():
        setattr(partner, key, value)
        
    db.commit()
    db.refresh(partner)
    log_audit(db, current_user.id, "UPDATE", "Partner", partner.id, partner_in.dict())
    return partner

@router.delete("/{partner_id}")
def delete_partner(partner_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    partner = db.query(Partner).filter(Partner.is_deleted == False).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    partner.is_deleted = True
    import datetime
    partner.deleted_at = datetime.datetime.utcnow()
    log_audit(db, current_user.id, "DELETE", "Partner", partner_id, {})
    db.commit()
    return {"status": "success"}
