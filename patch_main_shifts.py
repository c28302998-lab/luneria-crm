with open('backend/app/main.py', 'r') as f:
    content = f.read()

import re

# Insert import
if "from app.api import shifts" not in content:
    content = re.sub(r'from app\.api import (.*)', r'from app.api import \1\nfrom app.api import shifts', content, count=1)

# Insert router inclusion
if "shifts.router" not in content:
    last_include = content.rfind("app.include_router(")
    end_of_last_include = content.find(")", last_include) + 1
    content = content[:end_of_last_include] + '\napp.include_router(shifts.router, prefix="/api/v1/shifts", tags=["Shifts"])' + content[end_of_last_include:]

with open('backend/app/main.py', 'w') as f:
    f.write(content)
