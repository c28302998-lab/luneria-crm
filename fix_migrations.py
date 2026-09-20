with open("backend/app/main.py", "r") as f:
    content = f.read()

content = content.replace("            except Exception as e:\n                pass", "            except Exception as e:\n                conn.rollback()")

with open("backend/app/main.py", "w") as f:
    f.write(content)
