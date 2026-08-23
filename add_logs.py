import os
import re

files_to_patch = [
    ("backend/app/api/candidates.py", "Candidate"),
    ("backend/app/api/partners.py", "Partner"),
    ("backend/app/api/payments.py", "Payment"),
    ("backend/app/api/workers.py", "Worker")
]

for file, entity in files_to_patch:
    with open(file, "r") as f:
        content = f.read()
    
    if "db.commit()" in content and "def delete" in content:
        # Find where delete function ends and add log_audit
        content = re.sub(r'(db\.commit\(\)\n\s+return)', f'log_audit(db, current_user.id, "DELETE", "{entity}", {entity.lower()}_id, {{}})\n    \\1', content)
        with open(file, "w") as f:
            f.write(content)
