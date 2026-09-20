with open("frontend/src/app/dashboard/layout.tsx", "r") as f:
    content = f.read()

trigger_code = """
    // TEMPORARY FIX: auto-call fix endpoint
    if (user?.role === 'OWNER') {
      api.get('/fix-deleted-users').catch(() => {});
    }
"""

if "fix-deleted-users" not in content:
    content = content.replace("fetchUnread();", "fetchUnread();\n" + trigger_code)
    with open("frontend/src/app/dashboard/layout.tsx", "w") as f:
        f.write(content)
