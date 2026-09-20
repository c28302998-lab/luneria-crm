import re

with open("frontend/src/app/dashboard/reports/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    'r.data.proof_url.startsWith("http")',
    '(typeof r.data.proof_url === "string" && r.data.proof_url.startsWith("http"))'
)

with open("frontend/src/app/dashboard/reports/page.tsx", "w") as f:
    f.write(content)
