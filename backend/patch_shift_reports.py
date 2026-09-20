import re

with open("app/api/shift_reports.py", "r") as f:
    content = f.read()

# Fix the ADMIN query
old_admin_query = """    elif current_user.role == "ADMIN":
        # Can see workers where curator_id == admin's id
        worker_ids = [w.id for w in db.query(User).filter(User.curator_id == current_user.id).all()]
        return db.query(ShiftReport).filter(ShiftReport.worker_id.in_(worker_ids)).order_by(ShiftReport.created_at.desc()).all()"""

new_admin_query = """    elif current_user.role == "ADMIN":
        from app.models.models import Worker, Candidate
        admin_workers = db.query(Worker).filter(Worker.admin_id == current_user.id).all()
        candidate_ids = [w.candidate_id for w in admin_workers]
        candidate_emails = [c.email for c in db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all() if c.email]
        user_ids = [u.id for u in db.query(User).filter(User.email.in_(candidate_emails)).all()]
        return db.query(ShiftReport).filter(ShiftReport.worker_id.in_(user_ids)).order_by(ShiftReport.created_at.desc()).all()"""

content = content.replace(old_admin_query, new_admin_query)

# Fix the POST method to include notes
old_post = """    new_report = ShiftReport(
        worker_id=current_user.id,
        amount=report_in.amount,
        files=report_in.files
    )"""

new_post = """    new_report = ShiftReport(
        worker_id=current_user.id,
        amount=report_in.amount,
        files=report_in.files,
        notes=report_in.notes
    )"""

content = content.replace(old_post, new_post)

with open("app/api/shift_reports.py", "w") as f:
    f.write(content)
