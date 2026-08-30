from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, AccountRequest, Candidate
from app.schemas.schemas import AccountRequestCreate, AccountRequestUpdate, AccountRequestResponse
from app.core.dependencies import get_current_user, RoleChecker
from sqlalchemy import desc

router = APIRouter()

@router.post("/", response_model=AccountRequestResponse)
def create_request(req_in: AccountRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "CURATOR"]))):
    candidate = db.query(Candidate).filter(Candidate.id == req_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    req = AccountRequest(
        candidate_id=req_in.candidate_id,
        admin_id=current_user.id,
        admin_telegram=req_in.admin_telegram,
        comment=req_in.comment
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@router.get("/", response_model=List[AccountRequestResponse])
def get_requests(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR", "ADMIN"]))):
    query = db.query(AccountRequest).filter(AccountRequest.is_deleted == False).order_by(desc(AccountRequest.created_at))
    
    if current_user.role == "ADMIN":
        query = query.filter(AccountRequest.admin_id == current_user.id)
    
    return query.all()

@router.patch("/{req_id}/status", response_model=AccountRequestResponse)
def update_status(req_id: int, update: AccountRequestUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    req = db.query(AccountRequest).filter(AccountRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.status = update.status
    db.commit()
    db.refresh(req)
    return req
