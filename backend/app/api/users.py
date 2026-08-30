from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.models import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # All users can see the full list of users so they can use the chat system.
    # The frontend filters the chat list based on role hierarchy.
    users = db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserSchema)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    """
    Только OWNER может создавать пользователей (включая Curator, Admin, Finance).
    """
    user_db = db.query(User).filter(User.is_deleted == False).filter(User.email == user_in.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
        role=user_in.role,
        curator_id=user_in.curator_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_audit(db, current_user.id, "CREATE", "User", new_user.id, {"email": new_user.email, "role": new_user.role})
    return new_user

@router.get("/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.is_deleted == False).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == "CURATOR" and user.curator_id != current_user.id and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    user = db.query(User).filter(User.is_deleted == False).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
    for key, value in update_data.items():
        setattr(user, key, value)
        
    db.commit()
    db.refresh(user)
    log_audit(db, current_user.id, "UPDATE", "User", user.id, update_data)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    user = db.query(User).filter(User.is_deleted == False).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_deleted = True
    import datetime
    user.deleted_at = datetime.datetime.utcnow()
    user.status = "INACTIVE"
    
    log_audit(db, current_user.id, "DELETE", "User", user.id, {"is_deleted": True})
    db.commit()
    return {"ok": True}

from app.models.models import UserShift
from app.schemas.schemas import UserShift as UserShiftSchema, UserShiftWithUser
from datetime import datetime, date

@router.get("/shifts/current", response_model=Optional[UserShiftSchema])
def get_current_shift(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shift = db.query(UserShift).filter(
        UserShift.user_id == current_user.id,
        UserShift.end_time.is_(None)
    ).order_by(UserShift.start_time.desc()).first()
    return shift

@router.post("/shifts/start", response_model=UserShiftSchema)
def start_shift(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if already has active shift
    existing = db.query(UserShift).filter(UserShift.user_id == current_user.id, UserShift.end_time.is_(None)).first()
    if existing:
        return existing
        
    shift = UserShift(
        user_id=current_user.id,
        date=datetime.utcnow().date(),
        start_time=datetime.utcnow()
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift

@router.post("/shifts/end", response_model=UserShiftSchema)
def end_shift(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shifts = db.query(UserShift).filter(UserShift.user_id == current_user.id, UserShift.end_time.is_(None)).all()
    if not shifts:
        raise HTTPException(status_code=400, detail="No active shift")
        
    last_shift = None
    for shift in shifts:
        shift.end_time = datetime.utcnow()
        last_shift = shift
        
    db.commit()
    db.refresh(last_shift)
    return last_shift

@router.get("/shifts/all", response_model=List[UserShiftWithUser])
def get_all_shifts(target_date: date = None, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    query = db.query(UserShift)
    if target_date:
        query = query.filter(UserShift.date == target_date)
    return query.order_by(UserShift.start_time.desc()).all()
