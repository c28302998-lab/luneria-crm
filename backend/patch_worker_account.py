with open("app/api/workers.py", "r") as f:
    content = f.read()

import re

# Insert a new endpoint
new_endpoint = """@router.post("/{worker_id}/create-account")
def create_worker_account(worker_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    candidate = db.query(Candidate).filter(Candidate.id == worker.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if candidate.email:
        existing_user = db.query(User).filter(User.email == candidate.email).first()
        if existing_user:
            return {"email": existing_user.email, "message": "Аккаунт уже существует. Пароль был задан ранее."}

    import random
    import string
    from app.core.security import get_password_hash
    
    # Generate email if not exists
    if not candidate.email:
        candidate.email = f"worker{worker.id}@lunery.local"
        
    # Generate password
    new_password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
    
    new_user = User(
        email=candidate.email,
        hashed_password=get_password_hash(new_password),
        name=candidate.first_name or f"Worker {worker.id}",
        role="WORKER",
        telegram=candidate.telegram
    )
    db.add(new_user)
    db.commit()
    
    return {"email": candidate.email, "password": new_password, "message": "Успешно создано"}

"""

content = content + "\n" + new_endpoint

with open("app/api/workers.py", "w") as f:
    f.write(content)
