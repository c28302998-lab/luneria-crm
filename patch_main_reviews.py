with open('backend/app/main.py', 'r') as f:
    content = f.read()

import re

# Insert import
if "from app.api import reviews" not in content:
    content = re.sub(r'from app\.api import (.*)', r'from app.api import \1\nfrom app.api import reviews', content, count=1)

# Insert router inclusion
if "reviews.router" not in content:
    content = re.sub(r'(app\.include_router\(workers\.router,.*?\))', r'\1\napp.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews"])', content)

with open('backend/app/main.py', 'w') as f:
    f.write(content)
