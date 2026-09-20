with open("app/api/shift_reports.py", "r") as f:
    content = f.read()

import re

# Update get_reports permissions and logic
get_logic = """@router.get("/", response_model=List[ShiftReportResponse])
def get_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "WORKER":
        return db.query(ShiftReport).filter(ShiftReport.worker_id == current_user.id).order_by(ShiftReport.created_at.desc()).all()
    elif current_user.role == "OWNER" or current_user.role == "FINANCE":
        return db.query(ShiftReport).order_by(ShiftReport.created_at.desc()).all()
    elif current_user.role == "ADMIN":
        # Can see workers where curator_id == admin's id
        worker_ids = [w.id for w in db.query(User).filter(User.curator_id == current_user.id).all()]
        return db.query(ShiftReport).filter(ShiftReport.worker_id.in_(worker_ids)).order_by(ShiftReport.created_at.desc()).all()
    else:
        raise HTTPException(status_code=403, detail="Not allowed")"""

content = re.sub(r'@router\.get\("/", response_model=List\[ShiftReportResponse\]\)\ndef get_reports.*?return db\.query\(ShiftReport\)\.order_by\(ShiftReport\.created_at\.desc\(\)\)\.all\(\)', get_logic, content, flags=re.DOTALL)

with open("app/api/shift_reports.py", "w") as f:
    f.write(content)
