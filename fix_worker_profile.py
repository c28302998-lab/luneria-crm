import re

with open("frontend/src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

old_patch = "await api.patch(`/workers/${id}/info`, { [field]: value });"
new_patch = "await api.patch(`/workers/${id}/info`, null, { params: { [field]: value } });"

content = content.replace(old_patch, new_patch)

with open("frontend/src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
