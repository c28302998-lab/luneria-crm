with open("app/api/users.py", "r") as f:
    content = f.read()

content = content.replace("user.password_hash = get_password_hash(new_password)", "user.password_hash = get_password_hash(new_password)\n    user.raw_password = new_password")
content = content.replace("user_in.password", "user_in.password, raw_password=user_in.password")

with open("app/api/users.py", "w") as f:
    f.write(content)
