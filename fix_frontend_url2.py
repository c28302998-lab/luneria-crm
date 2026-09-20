import re

with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

content = content.replace("${API_URL}/telegram/proxy/accounts", "${api.defaults.baseURL}/telegram/proxy/accounts")
content = content.replace("import { api, API_URL } from '@/lib/api';", "import { api } from '@/lib/api';")

with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
