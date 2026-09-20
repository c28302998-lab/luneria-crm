import re

with open("app/api/reports.py", "r") as f:
    content = f.read()

content = content.replace(
    "return db.query(Report).offset(skip).limit(limit).all()",
    "return db.query(Report).filter(Report.is_deleted == False).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()"
)
content = content.replace(
    "return db.query(Report).filter(Report.admin_id == current_user.id).offset(skip).limit(limit).all()",
    "return db.query(Report).filter(Report.admin_id == current_user.id, Report.is_deleted == False).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()"
)

with open("app/api/reports.py", "w") as f:
    f.write(content)
