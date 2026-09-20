with open("app/api/shift_reports.py", "r") as f:
    content = f.read()

delete_endpoint = """
@router.delete("/{report_id}")
def delete_shift_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    report = db.query(ShiftReport).filter(ShiftReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.is_deleted = True
    db.commit()
    return {"message": "Deleted"}
"""

content += delete_endpoint

with open("app/api/shift_reports.py", "w") as f:
    f.write(content)
