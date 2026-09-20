with open("src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

import re
debug_code = """      const { data: workerData } = await api.get(`/workers/${id}`);
      console.log("WORKER DATA:", workerData);
      setWorker(workerData);
      setAccountInfo(workerData.account_info || '');"""
content = re.sub(r'const \{ data: workerData \} = await api\.get\(\`/workers/\$\{id\}\`\);\s*setWorker\(workerData\);\s*setAccountInfo\(workerData\.account_info \|\| \'\'\);', debug_code, content)

with open("src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
