with open("backend/app/main.py", "r") as f:
    content = f.read()

import re
content = re.sub(r'@app\.get\("/api/v1/fix-deleted-users"\)[\s\S]*?return \{"fixed": count\}', '', content)

with open("backend/app/main.py", "w") as f:
    f.write(content)
