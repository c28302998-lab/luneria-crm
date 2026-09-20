with open('backend/app/main.py', 'r') as f:
    content = f.read()

import re

# Find the last include_router
last_include = content.rfind("app.include_router(")
end_of_last_include = content.find(")", last_include) + 1

new_content = content[:end_of_last_include] + '\napp.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews"])' + content[end_of_last_include:]

with open('backend/app/main.py', 'w') as f:
    f.write(new_content)
