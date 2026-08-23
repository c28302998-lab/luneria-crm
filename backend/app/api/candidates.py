from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Candidate, CandidateHistory
from app.schemas.schemas import Candidate as CandidateSchema, CandidateCreate, CandidateUpdate, CandidateWithHistory
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[CandidateSchema])
def read_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "OWNER":
        candidates = db.query(Candidate).filter(Candidate.is_deleted == False).offset(skip).limit(limit).all()
    elif current_user.role == "CURATOR":
        admin_ids = [admin.id for admin in current_user.admins]
        candidates = db.query(Candidate).filter(Candidate.is_deleted == False).filter(Candidate.admin_id.in_(admin_ids)).offset(skip).limit(limit).all()
    elif current_user.role == "ADMIN":
        candidates = db.query(Candidate).filter(Candidate.is_deleted == False).filter(Candidate.admin_id == current_user.id).offset(skip).limit(limit).all()
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return candidates

@router.post("/", response_model=CandidateSchema)
def create_candidate(candidate_in: CandidateCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    admin_id = current_user.id if current_user.role == "ADMIN" else current_user.id # For OWNER it might be different but let's assume self
    
    new_candidate = Candidate(**candidate_in.dict(), admin_id=admin_id)
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    
    # Create History
    history = CandidateHistory(
        candidate_id=new_candidate.id, 
        new_status=new_candidate.status,
        changed_by=current_user.id,
        comment="Создан профиль"
    )
    db.add(history)
    db.commit()
    
    log_audit(db, current_user.id, "CREATE", "Candidate", new_candidate.id, {"status": new_candidate.status})
    return new_candidate

@router.get("/{candidate_id}", response_model=CandidateWithHistory)
def read_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from sqlalchemy.orm import joinedload
    candidate = db.query(Candidate).filter(Candidate.is_deleted == False).options(joinedload(Candidate.history)).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if current_user.role == "ADMIN" and candidate.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your candidate")
        
    if current_user.role == "CURATOR" and candidate.admin.curator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not in your team")
        
    return candidate

@router.put("/{candidate_id}", response_model=CandidateSchema)
def update_candidate(candidate_id: int, candidate_in: CandidateUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    candidate = db.query(Candidate).filter(Candidate.is_deleted == False).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if current_user.role == "ADMIN" and candidate.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your candidate")
        
    update_data = candidate_in.dict(exclude_unset=True)
    
    status_changed = False
    old_status = candidate.status
    if "status" in update_data and update_data["status"] != candidate.status:
        status_changed = True
        
    for key, value in update_data.items():
        setattr(candidate, key, value)
        
    db.commit()
    db.refresh(candidate)
    
    if status_changed:
        history = CandidateHistory(
            candidate_id=candidate.id, 
            old_status=old_status,
            new_status=candidate.status,
            changed_by=current_user.id
        )
        db.add(history)
        db.commit()
        
    log_audit(db, current_user.id, "UPDATE", "Candidate", candidate.id, update_data)
    return candidate

@router.patch("/{candidate_id}/status", response_model=CandidateSchema)
def change_status(candidate_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    candidate = db.query(Candidate).filter(Candidate.is_deleted == False).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if current_user.role == "ADMIN" and candidate.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your candidate")
        
    old_status = candidate.status
    candidate.status = status
    db.commit()
    db.refresh(candidate)
    
    history = CandidateHistory(
        candidate_id=candidate.id, 
        old_status=old_status,
        new_status=status,
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()
    
    log_audit(db, current_user.id, "CHANGE_STATUS", "Candidate", candidate.id, {"status": status})
    return candidate

@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    candidate = db.query(Candidate).filter(Candidate.is_deleted == False).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.is_deleted = True
    import datetime
    candidate.deleted_at = datetime.datetime.utcnow()
    log_audit(db, current_user.id, "DELETE", "Candidate", candidate_id, {})
    db.commit()
    return {"status": "success"}

import os
import shutil
from fastapi import UploadFile, File

UPLOAD_DIR = "uploads/candidates"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{candidate_id}/files")
def upload_file(
    candidate_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id, Candidate.is_deleted == False).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    # Security: Admins can only upload to their candidates, Owners/Curators to any
    if current_user.role == "ADMIN" and candidate.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{candidate_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # URL to access the file (served as static files)
    file_url = f"/uploads/candidates/{candidate_id}_{file.filename}"
    
    # Update candidate files array
    files_list = list(candidate.files) if candidate.files else []
    files_list.append(file_url)
    
    # Needs this to detect JSON mutation in SQLAlchemy
    candidate.files = files_list
    
    db.commit()
    db.refresh(candidate)
    
    return {"ok": True, "url": file_url}
