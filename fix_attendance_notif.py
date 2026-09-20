import re

with open("backend/app/api/attendance.py", "r") as f:
    content = f.read()

# Add import if missing
if "from app.models.models import" in content and "Notification" not in content:
    content = content.replace("from app.models.models import", "from app.models.models import Notification,")

# Add notification creation logic to start_shift
old_code = """    db.add(record)
    db.commit()
    db.refresh(record)
    return record"""

new_code = """    db.add(record)
    
    # Send notification to Admin
    if worker.admin_id:
        notif = Notification(
            user_id=worker.admin_id,
            type="Выход на смену",
            message=f"Работник {candidate.first_name} ({current_user.email}) вышел на смену и ждет подтверждения."
        )
        db.add(notif)
        
    db.commit()
    db.refresh(record)
    return record"""

content = content.replace(old_code, new_code)

with open("backend/app/api/attendance.py", "w") as f:
    f.write(content)
