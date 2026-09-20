import re

with open("backend/app/api/shift_reports.py", "r") as f:
    content = f.read()

# Fix 1: Save notes
old_create = """    new_report = ShiftReport(
        worker_id=current_user.id,
        amount=report_in.amount,
        files=report_in.files,
        status="PENDING"
    )"""

new_create = """    new_report = ShiftReport(
        worker_id=current_user.id,
        amount=report_in.amount,
        files=report_in.files,
        notes=report_in.notes,
        status="PENDING"
    )"""

content = content.replace(old_create, new_create)

# Fix 2: Populate worker_name and admin_name in get_reports
# Wait, get_reports returns db.query(ShiftReport)...all()
# I need to manually map them or attach properties.
# Since ShiftReportResponse has worker_name, we can just attach it to the SQLAlchemy object before returning, or return a list of dicts.
# Let's replace the whole get_reports function.
