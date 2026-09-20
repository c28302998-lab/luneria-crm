with open("app/api/router.py", "r") as f:
    content = f.read()

import re

# Add import
if "from app.api import balance_requests" not in content:
    content = content.replace("from app.api import auth", "from app.api import auth, balance_requests")

# Add include_router
if "prefix=\"/balance-requests\"" not in content:
    content = content.replace("api_router.include_router(auth.router, tags=[\"auth\"])", "api_router.include_router(auth.router, tags=[\"auth\"])\napi_router.include_router(balance_requests.router, prefix=\"/balance-requests\", tags=[\"balance-requests\"])")

with open("app/api/router.py", "w") as f:
    f.write(content)
