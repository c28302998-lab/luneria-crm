import re

with open("backend/app/core/dependencies.py", "r") as f:
    content = f.read()

content = content.replace(
    'status_code=status.HTTP_403_FORBIDDEN,\n            detail="Could not validate credentials"',
    'status_code=status.HTTP_401_UNAUTHORIZED,\n            detail="Could not validate credentials",\n            headers={"WWW-Authenticate": "Bearer"}'
)

with open("backend/app/core/dependencies.py", "w") as f:
    f.write(content)
