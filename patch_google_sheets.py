with open("backend/app/services/google_sheets.py", "r") as f:
    content = f.read()

import re
# Replace the hardcoded DEFAULT_CREDS with a fallback
content = re.sub(r'DEFAULT_CREDS = \{.*?\}', 'DEFAULT_CREDS = {"type": "service_account"}', content, flags=re.DOTALL)

with open("backend/app/services/google_sheets.py", "w") as f:
    f.write(content)
