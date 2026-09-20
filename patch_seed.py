import re

with open("backend/seed.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "conn.execute(text(\"ALTER TABLE" in line and "try:" not in line:
        indent = len(line) - len(line.lstrip())
        new_lines.append(" " * indent + "try:\n")
        new_lines.append(" " * (indent + 4) + line.lstrip())
        new_lines.append(" " * indent + "except:\n")
        new_lines.append(" " * (indent + 4) + "pass\n")
    elif "conn.execute(text(f\"ALTER TABLE" in line:
        indent = len(line) - len(line.lstrip())
        new_lines.append(" " * indent + "try:\n")
        new_lines.append(" " * (indent + 4) + line.lstrip())
        new_lines.append(" " * indent + "except:\n")
        new_lines.append(" " * (indent + 4) + "pass\n")
    elif "conn.execute(text(f\"UPDATE" in line:
        indent = len(line) - len(line.lstrip())
        new_lines.append(" " * indent + "try:\n")
        new_lines.append(" " * (indent + 4) + line.lstrip())
        new_lines.append(" " * indent + "except:\n")
        new_lines.append(" " * (indent + 4) + "pass\n")
    else:
        new_lines.append(line)

with open("backend/seed.py", "w") as f:
    f.writelines(new_lines)
