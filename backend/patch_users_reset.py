with open("app/api/users.py", "r") as f:
    content = f.read()

new_endpoint = """
@router.post("/{user_id}/reset-password")
def reset_user_password(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    import random
    import string
    from app.core.security import get_password_hash
    
    new_password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Пароль сброшен", "password": new_password}
"""

content = content + new_endpoint

with open("app/api/users.py", "w") as f:
    f.write(content)
