from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import AdminPayout, User
from app.schemas.schemas import AdminPayout as AdminPayoutSchema, AdminPayoutCreate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[AdminPayoutSchema])
def read_admin_payouts(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE", "ADMIN"]))):
    if current_user.role == "ADMIN":
        return db.query(AdminPayout).filter(AdminPayout.is_deleted == False, AdminPayout.admin_id == current_user.id).order_by(AdminPayout.date.desc()).offset(skip).limit(limit).all()
    return db.query(AdminPayout).filter(AdminPayout.is_deleted == False).order_by(AdminPayout.date.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=AdminPayoutSchema)
def create_admin_payout(payout_in: AdminPayoutCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    admin = db.query(User).filter(User.id == payout_in.admin_id, User.role == "ADMIN").first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
        
    payout = AdminPayout(
        admin_id=payout_in.admin_id,
        amount=payout_in.amount,
        date=payout_in.date,
        description=payout_in.description,
        created_by=current_user.id
    )
    db.add(payout)
    
    # Optionally update admin balance if needed. 
    # But usually a payout *decreases* the owed balance or just tracks it.
    # The prompt says "чтоб овнер мог руками добавлять баланс админам"
    # Wait, if they are adding a payout, it means they are recording that they paid the admin.
    admin.balance -= payout_in.amount
    
    db.commit()
    db.refresh(payout)
    log_audit(db, current_user.id, "CREATE", "AdminPayout", payout.id, {"amount": payout.amount})
    return payout

@router.delete("/{payout_id}")
def delete_admin_payout(payout_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    payout = db.query(AdminPayout).filter(AdminPayout.is_deleted == False, AdminPayout.id == payout_id).first()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    admin = db.query(User).filter(User.id == payout.admin_id).first()
    if admin:
        admin.balance += payout.amount
        
    payout.is_deleted = True
    import datetime
    payout.deleted_at = datetime.datetime.utcnow()
    log_audit(db, current_user.id, "DELETE", "AdminPayout", payout_id, {})
    db.commit()
    return {"status": "success"}
