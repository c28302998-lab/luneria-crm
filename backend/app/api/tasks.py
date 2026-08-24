import uuid
import os, shutil
from fastapi import UploadFile, File
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import FileUpload, User, Task, Notification
from app.schemas.schemas import Task as TaskSchema, TaskCreate, TaskUpdate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[TaskSchema])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Task).filter(Task.is_deleted == False)
    if current_user.role == "OWNER":
        return query.offset(skip).limit(limit).all()
    elif current_user.role == "CURATOR":
        return query.filter(
            (Task.assigned_user_id == current_user.id) | (Task.creator_id == current_user.id)
        ).offset(skip).limit(limit).all()
    else:
        return query.filter(Task.assigned_user_id == current_user.id).offset(skip).limit(limit).all()

@router.post("/", response_model=TaskSchema)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    task = Task(**task_in.dict(), creator_id=current_user.id)
    db.add(task)
    
    db.commit()
    db.refresh(task)
    
    # Send notification
    notif = Notification(user_id=task.assigned_user_id, type="Новая задача", message=f"Вам назначена новая задача: {task.title}")
    db.add(notif)
    db.commit()

    log_audit(db, current_user.id, "CREATE", "Task", task.id, {"title": task.title, "assigned_to": task.assigned_user_id})
    return task

@router.put("/{task_id}", response_model=TaskSchema)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.is_deleted == False).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if current_user.role != "OWNER" and task.assigned_user_id != current_user.id and task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    for key, value in task_in.dict(exclude_unset=True).items():
        setattr(task, key, value)
        
    
    db.commit()
    db.refresh(task)
    
    # Send notification
    notif = Notification(user_id=task.assigned_user_id, type="Новая задача", message=f"Вам назначена новая задача: {task.title}")
    db.add(notif)
    db.commit()

    log_audit(db, current_user.id, "UPDATE", "Task", task.id, task_in.dict(exclude_unset=True))
    return task


UPLOAD_DIR = "uploads/tasks"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{task_id}/files")
def upload_file(
    task_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    file_id = str(uuid.uuid4())
    file_record = FileUpload(
        id=file_id,
        filename=file.filename,
        content_type=file.content_type,
        data=file.file.read()
    )
    db.add(file_record)
        
    file_url = f"/files/{file_id}"
    
    files_list = list(task.files) if task.files else []
    files_list.append(file_url)
    task.files = files_list
    
    db.commit()
    return {"ok": True, "url": file_url}

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    task = db.query(Task).filter(Task.is_deleted == False).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.is_deleted = True
    db.commit()
    log_audit(db, current_user.id, "DELETE", "Task", task.id, {"title": task.title})
    return {"ok": True}
