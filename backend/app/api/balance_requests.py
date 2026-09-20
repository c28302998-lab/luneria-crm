from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import BalanceRequest, User
from app.core.dependencies import get_current_user, RoleChecker
from pydantic import BaseModel

router = APIRouter()

class BalanceRequestCreate(BaseModel):
    worker_id: int
    type: str
    amount: float
    reason: str
    proof_url: str | None = None

class BalanceRequestUpdate(BaseModel):
    status: str # APPROVED, REJECTED

@router.get("/")
def get_balance_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "OWNER":
        return db.query(BalanceRequest).order_by(BalanceRequest.created_at.desc()).all()
    elif current_user.role == "ADMIN":
        return db.query(BalanceRequest).filter(BalanceRequest.admin_id == current_user.id).order_by(BalanceRequest.created_at.desc()).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.post("/")
def create_balance_request(req: BalanceRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN"]))):
    br = BalanceRequest(
        worker_id=req.worker_id,
        admin_id=current_user.id,
        type=req.type,
        amount=req.amount,
        reason=req.reason,
        proof_url=req.proof_url
    )
    db.add(br)
    db.commit()
    db.refresh(br)
    return br

@router.put("/{req_id}/status")
def update_balance_request(req_id: int, req: BalanceRequestUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    br = db.query(BalanceRequest).filter(BalanceRequest.id == req_id).first()
    if not br:
        raise HTTPException(status_code=404, detail="Request not found")
    if br.status != "PENDING":
        raise HTTPException(status_code=400, detail="Already processed")
        
    br.status = req.status
    if req.status == "APPROVED":
        worker = db.query(User).filter(User.id == br.worker_id).first()
        if worker:
            if br.type == "FINE":
                worker.balance = (worker.balance or 0.0) - br.amount
            elif br.type == "BONUS":
                worker.balance = (worker.balance or 0.0) + br.amount
    db.commit()
    return br
