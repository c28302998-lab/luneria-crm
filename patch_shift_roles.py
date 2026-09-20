with open('backend/app/api/shifts.py', 'r') as f:
    content = f.read()

content = content.replace(
    'def approve_shift(shift_id: int, payload: ShiftApproveRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "ADMIN"]))):',
    'def approve_shift(shift_id: int, payload: ShiftApproveRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):'
)

with open('backend/app/api/shifts.py', 'w') as f:
    f.write(content)
