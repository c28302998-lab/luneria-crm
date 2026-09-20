with open("backend/app/api/workers.py", "r") as f:
    content = f.read()

fix_endpoint = """
@router.get("/tools/fix-deleted-users")
def fix_deleted_users(db: Session = Depends(get_db)):
    from app.models.models import User
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

if "/tools/fix-deleted-users" not in content:
    content += fix_endpoint
    with open("backend/app/api/workers.py", "w") as f:
        f.write(content)
