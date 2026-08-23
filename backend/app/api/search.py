from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.models.models import User, Candidate, Worker, Partner
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/")
def global_search(q: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Very basic search implementation
    search_term = f"%{q}%"
    
    candidates = db.query(Candidate).filter(
        (Candidate.first_name.ilike(search_term)) | 
        (Candidate.email.ilike(search_term)) | 
        (Candidate.telegram.ilike(search_term))
    ).all()
    
    partners = db.query(Partner).filter(Partner.company_name.ilike(search_term)).all()
    
    # Needs proper RBAC filtering based on current_user role
    return {
        "candidates": [{"id": c.id, "name": c.first_name, "type": "Candidate"} for c in candidates],
        "partners": [{"id": p.id, "name": p.company_name, "type": "Partner"} for p in partners]
    }
