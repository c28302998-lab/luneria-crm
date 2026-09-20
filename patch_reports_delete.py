with open("backend/app/api/reports.py", "r") as f:
    content = f.read()

delete_endpoint = """
@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["OWNER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return {"status": "success"}
"""

if "def delete_report" not in content:
    content += delete_endpoint
    with open("backend/app/api/reports.py", "w") as f:
        f.write(content)
