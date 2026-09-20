from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User, Task, AuditLog
from app.models.telegram import AccountReview, TelegramAccount, AccountAssignment
from app.core.dependencies import get_current_user, RoleChecker
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ReviewSubmit(BaseModel):
    potential: str # HIGH, MEDIUM, LOW
    decision: str # REASSIGN, RE_REGISTER, ARCHIVE
    comment: str = ""

@router.post("/{review_id}/submit")
def submit_review(review_id: int, req: ReviewSubmit, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    review = db.query(AccountReview).filter(AccountReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    if review.completed_at:
        raise HTTPException(status_code=400, detail="Review already completed")
        
    review.potential = req.potential
    review.decision = req.decision
    review.comment = req.comment
    review.completed_at = datetime.utcnow()
    
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == review.account_id).first()
    
    # Process decision
    if req.decision == "ARCHIVE":
        if acc:
            acc.status = "ARCHIVED"
    elif req.decision == "RE_REGISTER":
        if acc:
            acc.status = "DISABLED"
        # Auto-create task for re-registration
        task = Task(
            title=f"Перерегистрация аккаунта {acc.name if acc else review.account_id}",
            description=f"Аккаунт {acc.id} отправлен на перерегистрацию по итогам ревью.",
            priority="HIGH",
            assigned_user_id=current_user.id,
            creator_id=1,
            status="NEW"
        )
        db.add(task)
    elif req.decision == "REASSIGN":
        if acc:
            # It just stays available (no active assignment, status ACTIVE)
            acc.status = "ACTIVE"
            
    # Audit
    log = AuditLog(
        user_id=current_user.id,
        action="ACCOUNT_REVIEW_COMPLETED",
        changes={"message": f"Review {review.id} for Account {review.account_id} completed. Decision: {req.decision}"},
    )
    db.add(log)
    
    db.commit()
    return {"message": "Review submitted successfully"}

@router.get("/")
def list_reviews(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    return db.query(AccountReview).order_by(AccountReview.created_at.desc()).all()
