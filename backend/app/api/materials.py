import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os, shutil

from app.db.database import get_db
from app.models.models import FileUpload, User, Material
from app.schemas.schemas import Material as MaterialSchema, MaterialCreate, MaterialUpdate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[MaterialSchema])
def read_materials(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Material).filter(Material.is_deleted == False).order_by(Material.created_at.asc()).offset(skip).limit(limit).all()

@router.post("/", response_model=MaterialSchema)
def create_material(material_in: MaterialCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    material = Material(**material_in.dict(), created_by=current_user.id)
    db.add(material)
    db.commit()
    db.refresh(material)
    log_audit(db, current_user.id, "CREATE", "Material", material.id, {"title": material.title})
    return material

@router.put("/{material_id}", response_model=MaterialSchema)
def update_material(material_id: int, material_in: MaterialUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    material = db.query(Material).filter(Material.is_deleted == False).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
        
    for key, value in material_in.dict(exclude_unset=True).items():
        setattr(material, key, value)
        
    db.commit()
    db.refresh(material)
    log_audit(db, current_user.id, "UPDATE", "Material", material.id, {"title": material.title})
    return material

@router.delete("/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    material = db.query(Material).filter(Material.is_deleted == False).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
        
    material.is_deleted = True
    db.commit()
    log_audit(db, current_user.id, "DELETE", "Material", material.id, {"title": material.title})
    return {"ok": True}

UPLOAD_DIR = "uploads/materials"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{material_id}/files")
def upload_file(
    material_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))
):
    material = db.query(Material).filter(Material.id == material_id, Material.is_deleted == False).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
        
    file_id = str(uuid.uuid4())
    file_record = FileUpload(
        id=file_id,
        filename=file.filename,
        content_type=file.content_type,
        data=file.file.read()
    )
    db.add(file_record)
        
    file_url = f"/files/{file_id}"
    
    files_list = list(material.files) if material.files else []
    files_list.append(file_url)
    material.files = files_list
    
    db.commit()
    return {"ok": True, "url": file_url}
