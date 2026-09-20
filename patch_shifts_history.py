with open('backend/app/api/shifts.py', 'r') as f:
    content = f.read()

new_endpoint = """
@router.get("/all")
def get_all_shifts(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):
    query = db.query(Shift).filter(Shift.status != "ACTIVE") # Show all completed/pending/approved
    if current_user.role == "ADMIN":
        query = query.filter(Shift.admin_id == current_user.id)
    return query.order_by(Shift.start_time.desc()).limit(200).all()
"""

if "@router.get(\"/all\")" not in content:
    content += "\n" + new_endpoint

with open('backend/app/api/shifts.py', 'w') as f:
    f.write(content)
