import re

with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "setGlobalSearchResult(data);",
    "setGlobalSearchResult({ ...data, name: data.title });"
)

with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
