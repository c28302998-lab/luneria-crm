from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User
from app.schemas.user import Token, User as UserSchema
from app.core.security import verify_password, create_access_token
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
    ip = form_data.username # We use username as key since we don't have request.client.host easily here without Request object.
    
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
            
    user = db.query(User).filter(User.is_deleted == False).filter(User.email == form_data.username).first()
    
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
