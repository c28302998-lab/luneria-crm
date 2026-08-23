from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Comment, Candidate, Task
from app.schemas.schemas import Comment as CommentSchema, CommentCreate
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/{entity_type}", response_model=List[CommentSchema])
def get_all_comments_by_type(entity_type: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Comment).filter(Comment.entity_type == entity_type.upper()).all()


@router.get("/{entity_type}/{entity_id}", response_model=List[CommentSchema])
def get_comments(entity_type: str, entity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Comment).filter(Comment.entity_type == entity_type.upper(), Comment.entity_id == entity_id).all()

@router.post("/{entity_type}/{entity_id}", response_model=CommentSchema)
def add_comment(entity_type: str, entity_id: int, comment_in: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = Comment(
        entity_type=entity_type.upper(),
        entity_id=entity_id,
        user_id=current_user.id,
        text=comment_in.text
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
