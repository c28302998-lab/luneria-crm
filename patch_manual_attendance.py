with open("backend/app/api/attendance.py", "r") as f:
    content = f.read()

content = content.replace("record.is_present = attendance_in.is_present\n        record.updated_by = current_user.id", "record.is_present = attendance_in.is_present\n        record.status = 'APPROVED'\n        record.updated_by = current_user.id")

content = content.replace("is_present=attendance_in.is_present,\n            updated_by=current_user.id", "is_present=attendance_in.is_present,\n            status='APPROVED',\n            updated_by=current_user.id")

with open("backend/app/api/attendance.py", "w") as f:
    f.write(content)
