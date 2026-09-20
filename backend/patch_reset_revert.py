with open("app/api/workers.py", "r") as f:
    content = f.read()

import re

new_logic = """    import random
    import string
    from app.core.security import get_password_hash
    
    new_password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=6))

    if candidate.email:
        existing_user = db.query(User).filter(User.email == candidate.email).first()
        if existing_user:
            existing_user.password_hash = get_password_hash(new_password)
            db.commit()
            return {"email": existing_user.email, "password": new_password, "message": "Новый пароль успешно сгенерирован!"}"""

old_logic = """    if candidate.email:
        existing_user = db.query(User).filter(User.email == candidate.email).first()
        if existing_user:
            return {"email": existing_user.email, "message": "Аккаунт уже существует. Пароль был задан ранее."}

    import random
    import string
    from app.core.security import get_password_hash
    
    new_password = "Pass_" + "".join(random.choices(string.ascii_letters + string.digits, k=6))"""

content = content.replace(new_logic, old_logic)

with open("app/api/workers.py", "w") as f:
    f.write(content)
