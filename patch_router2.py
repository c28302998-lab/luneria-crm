with open("backend/app/api/router.py", "r") as f:
    content = f.read()

import re

# Add import
if "from app.api import balance_requests" not in content:
    content = content.replace("from app.api import (", "from app.api import balance_requests,\n(")

# Add include_router
if "prefix=\"/balance-requests\"" not in content:
    content = content + "\napi_router.include_router(balance_requests.router, prefix=\"/balance-requests\", tags=[\"balance-requests\"])\n"

with open("backend/app/api/router.py", "w") as f:
    f.write(content)
