from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Training
from app.schemas.schemas import Training as TrainingSchema, TrainingUpdate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/{candidate_id}", response_model=TrainingSchema)
def read_training(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    training = db.query(Training).filter(Training.candidate_id == candidate_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    return training

@router.put("/{training_id}", response_model=TrainingSchema)
def update_training(training_id: int, training_in: TrainingUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
        
    for key, value in training_in.dict(exclude_unset=True).items():
        setattr(training, key, value)
        
    db.commit()
    db.refresh(training)
    log_audit(db, current_user.id, "UPDATE", "Training", training.id, {"progress": training.progress})
    return training
