import re

with open('backend/app/api/workers.py', 'r') as f:
    content = f.read()

old_func_pattern = r"@router\.post\(\"/\{worker_id\}/create-account\"\).*?return {\"email\": candidate.email, \"password\": new_password, \"message\": \"Успешно создано\"}"

new_func = """@router.post("/{worker_id}/create-account")
def create_worker_account(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    candidate = db.query(Candidate).filter(Candidate.id == worker.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if not candidate.email:
        raise HTTPException(status_code=400, detail="Кандидат не имеет email")

    existing_user = db.query(User).filter(User.email == candidate.email).first()
    if not existing_user:
        new_user = User(
            email=candidate.email,
            name=candidate.first_name,
            role="WORKER",
            raw_password=None
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        existing_user = new_user

    # Generate Invite Token
    import uuid
    from datetime import datetime, timedelta
    from app.models.models import InviteToken
    token = str(uuid.uuid4())
    invite = InviteToken(
        token=token,
        user_id=existing_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invite)
    db.commit()
    
    return {"email": candidate.email, "invite_link": f"/invite/{token}", "message": "Приглашение создано"}"""

content = re.sub(old_func_pattern, new_func, content, flags=re.DOTALL)

with open('backend/app/api/workers.py', 'w') as f:
    f.write(content)
