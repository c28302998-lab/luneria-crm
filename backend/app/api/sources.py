import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os, shutil

from app.db.database import get_db
from app.models.models import FileUpload, User, Source
from app.schemas.schemas import Source as SourceSchema, SourceCreate, SourceUpdate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[SourceSchema])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Source).filter(Source.is_deleted == False).order_by(Source.created_at.asc()).offset(skip).limit(limit).all()

@router.post("/", response_model=SourceSchema)
def create_source(source_in: SourceCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    source = Source(**source_in.dict(), created_by=current_user.id)
    db.add(source)
    db.commit()
    db.refresh(source)
    log_audit(db, current_user.id, "CREATE", "Source", source.id, {"title": source.title})
    return source

@router.put("/{source_id}", response_model=SourceSchema)
def update_source(source_id: int, source_in: SourceUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    source = db.query(Source).filter(Source.is_deleted == False).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    for key, value in source_in.dict(exclude_unset=True).items():
        setattr(source, key, value)
        
    db.commit()
    db.refresh(source)
    log_audit(db, current_user.id, "UPDATE", "Source", source.id, {"title": source.title})
    return source

@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    source = db.query(Source).filter(Source.is_deleted == False).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    source.is_deleted = True
    db.commit()
    log_audit(db, current_user.id, "DELETE", "Source", source.id, {"title": source.title})
    return {"ok": True}

UPLOAD_DIR = "uploads/sources"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{source_id}/files")
def upload_file(
    source_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))
):
    source = db.query(Source).filter(Source.id == source_id, Source.is_deleted == False).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    file_id = str(uuid.uuid4())
    file_record = FileUpload(
        id=file_id,
        filename=file.filename,
        content_type=file.content_type,
        data=file.file.read()
    )
    db.add(file_record)
        
    file_url = f"/files/{file_id}"
    
    files_list = list(source.files) if source.files else []
    files_list.append(file_url)
    source.files = files_list
    
    db.commit()
    return {"ok": True, "url": file_url}
