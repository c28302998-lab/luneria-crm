import re

with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

# Replace hardcoded backend URL with API_URL
# First, ensure API_URL is imported from @/lib/api
if "API_URL" not in content:
    content = content.replace("import { api } from '@/lib/api';", "import { api, API_URL } from '@/lib/api';")

# Replace https://lunery-backend.onrender.com/api/v1 with ${API_URL}
content = content.replace("https://lunery-backend.onrender.com/api/v1/telegram/proxy/accounts", "${API_URL}/telegram/proxy/accounts")

with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
