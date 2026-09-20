with open("backend/app/api/auth.py", "r") as f:
    content = f.read()

import re

old_query = "user = db.query(User).filter(User.is_deleted == False).filter(User.email == form_data.username).first()"
new_query = "user = db.query(User).filter(User.is_deleted == False).filter(User.email.ilike(form_data.username.strip())).first()"

content = content.replace(old_query, new_query)

with open("backend/app/api/auth.py", "w") as f:
    f.write(content)
