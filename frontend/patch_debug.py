with open("src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

import re
debug_code = """    } catch (err: any) {
      console.error("DEBUG FETCH ERROR:", err);
      if (err.response?.status === 404 || err.response?.status === 403) {"""
content = re.sub(r'\} catch \(err: any\) \{\s*console\.error\(err\);\s*if \(err\.response\?\.status', debug_code, content)

# Fix PATCH
patch_code = """  const handleInfoChange = async (field: 'account_info' | 'shift', value: string) => {
    try {
      await api.patch(`/workers/${id}/info`, { [field]: value });"""
content = re.sub(r'const handleInfoChange = async \(field: \'account_info\' \| \'shift\', value: string\) => \{\s*try \{\s*await api\.put\(\`/workers/\$\{id\}\`, \{ \[field\]: value \}\);', patch_code, content)

with open("src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
