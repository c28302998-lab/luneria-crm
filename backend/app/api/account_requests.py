from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, AccountRequest, Candidate, Worker
from app.schemas.schemas import AccountRequestCreate, AccountRequestUpdate, AccountRequestResponse
from app.core.dependencies import get_current_user, RoleChecker
from sqlalchemy import desc

router = APIRouter()

@router.post("/", response_model=AccountRequestResponse)
def create_request(req_in: AccountRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN", "CURATOR"]))):
    req = AccountRequest(
        admin_id=current_user.id,
        candidate_name=req_in.candidate_name,
        age=req_in.age,
        account_type=req_in.account_type,
        admin_nickname=req_in.admin_nickname,
        candidate_nickname=req_in.candidate_nickname,
        candidate_tg=req_in.candidate_tg,
        questionnaire=req_in.questionnaire,
        candidate_id=req_in.candidate_id
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@router.get("/", response_model=List[AccountRequestResponse])
def get_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(AccountRequest).filter(AccountRequest.is_deleted == False).order_by(desc(AccountRequest.created_at))
    
    if current_user.role == "ADMIN":
        query = query.filter(AccountRequest.admin_id == current_user.id)
    # Curators see everything? Or just their admins? The user said "а у Куратора и Овнера отображалась эта заявка". We will let Curators see all.
    
    return query.all()

@router.patch("/{req_id}/status", response_model=AccountRequestResponse)
def update_status(req_id: int, update: AccountRequestUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    try:
            req = db.query(AccountRequest).filter(AccountRequest.id == req_id).first()
            if not req:
                raise HTTPException(status_code=404, detail="Request not found")
                
            if update.status:
                req.status = update.status
                # Если статус меняется на ISSUED и есть кандидат, автоматически переводим его в работники
                if update.status == "ISSUED" and req.candidate_id:
                    existing_worker = db.query(Worker).filter(Worker.candidate_id == req.candidate_id).first()
                    if not existing_worker:
                        worker = Worker(
                            candidate_id=req.candidate_id,
                            admin_id=req.admin_id,
                            partner_id=req.partner_id
                        )
                        db.add(worker)
                        candidate = db.query(Candidate).filter(Candidate.id == req.candidate_id).first()
                        if candidate:
                            candidate.status = "WORKER"
        
            if update.partner_id is not None:
                req.partner_id = update.partner_id
            if update.issued_account_name is not None:
                req.issued_account_name = update.issued_account_name
                
            db.commit()
            db.refresh(req)
            # Manual serialization to catch Pydantic errors
            try:
                resp = AccountRequestResponse.from_orm(req)
                return resp
            except Exception as e:
                raise Exception(f"Serialization error: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.delete("/{req_id}")
def delete_request(req_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    req = db.query(AccountRequest).filter(AccountRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.is_deleted = True
    db.commit()
    return {"message": "Deleted"}
