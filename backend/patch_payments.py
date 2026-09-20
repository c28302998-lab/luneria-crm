with open("app/api/payments.py", "r") as f:
    content = f.read()

new_func = """def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE", "ADMIN"]))):
    query = db.query(Payment).filter(Payment.is_deleted == False)
    if current_user.role == "ADMIN":
        query = query.filter(Payment.admin_id == current_user.id)
    return query.order_by(Payment.date.desc()).offset(skip).limit(limit).all()"""

import re
content = re.sub(r'def read_payments.*?return db\.query\(Payment\).*?\.all\(\)', new_func, content, flags=re.DOTALL)

with open("app/api/payments.py", "w") as f:
    f.write(content)
