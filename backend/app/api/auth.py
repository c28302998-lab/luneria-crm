from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User
from app.schemas.user import Token, User as UserSchema
from app.core.security import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.dependencies import get_current_user

router = APIRouter()

import time
login_attempts = {}

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    ip = form_data.username.strip() # We use username as key since we don't have request.client.host easily here without Request object.
    
    # Rate limiting logic (simple brute-force protection)
    now = time.time()
    if ip in login_attempts:
        attempts, first_attempt_time = login_attempts[ip]
        if now - first_attempt_time > 300: # Reset after 5 minutes
            login_attempts[ip] = (0, now)
        elif attempts >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Please try again in 5 minutes."
            )
            
    user = db.query(User).filter(User.is_deleted == False).filter(User.email.ilike(form_data.username.strip())).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        if ip in login_attempts:
            login_attempts[ip] = (login_attempts[ip][0] + 1, login_attempts[ip][1])
        else:
            login_attempts[ip] = (1, now)
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    
    # Reset on success
    if ip in login_attempts:
        del login_attempts[ip]
        
    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user.
    """
    return current_user

from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.core.security import get_password_hash
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Текущий пароль неверен")
    
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"ok": True}

from app.models.models import InviteToken
from datetime import datetime

class InviteAcceptRequest(BaseModel):
    token: str
    password: str

@router.post("/invite/accept")
def accept_invite(req: InviteAcceptRequest, db: Session = Depends(get_db)):
    invite = db.query(InviteToken).filter(InviteToken.token == req.token).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid token")
    if invite.is_used:
        raise HTTPException(status_code=400, detail="Token already used")
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")
        
    user = db.query(User).filter(User.id == invite.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.password_hash = get_password_hash(req.password)
    user.raw_password = None # Clear raw password
    invite.is_used = True
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role}}

