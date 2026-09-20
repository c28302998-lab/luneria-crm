import re

with open("app/api/shift_reports.py", "r") as f:
    content = f.read()

content = content.replace(
    "filter(ShiftReport.worker_id == current_user.id).order_by",
    "filter(ShiftReport.worker_id == current_user.id, ShiftReport.is_deleted == False).order_by"
)
content = content.replace(
    "return db.query(ShiftReport).order_by(ShiftReport.created_at.desc()).all()",
    "return db.query(ShiftReport).filter(ShiftReport.is_deleted == False).order_by(ShiftReport.created_at.desc()).all()"
)
content = content.replace(
    "filter(ShiftReport.worker_id.in_(user_ids)).order_by",
    "filter(ShiftReport.worker_id.in_(user_ids), ShiftReport.is_deleted == False).order_by"
)

with open("app/api/shift_reports.py", "w") as f:
    f.write(content)
