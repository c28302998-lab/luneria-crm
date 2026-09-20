with open("backend/app/main.py", "r") as f:
    content = f.read()

fix_code = """
@app.get("/api/fix-deleted-users")
def fix_deleted_users(db: Session = Depends(get_db)):
    from app.models.models import Worker, User
    deleted_workers = db.query(Worker).filter(Worker.is_deleted == True).all()
    count = 0
    for w in deleted_workers:
        if w.candidate and w.candidate.email:
            u = db.query(User).filter(User.email == w.candidate.email).first()
            if u and not u.is_deleted:
                u.is_deleted = True
                count += 1
    db.commit()
    return {"fixed": count}
"""

if "/api/fix-deleted-users" not in content:
    content += fix_code
    with open("backend/app/main.py", "w") as f:
        f.write(content)
