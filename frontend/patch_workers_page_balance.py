import re

with open("src/app/dashboard/workers/page.tsx", "r") as f:
    content = f.read()

old_logic = """      const uMap: Record<number, string> = {};
      usersRes.data.forEach((u: any) => {
        uMap[u.id] = u.name;
      });
      setUsersMap(uMap);"""

new_logic = """      const uMap: Record<number, any> = {};
      usersRes.data.forEach((u: any) => {
        uMap[u.id] = u;
      });
      setUsersMap(uMap);"""

content = content.replace(old_logic, new_logic)

with open("src/app/dashboard/workers/page.tsx", "w") as f:
    f.write(content)
