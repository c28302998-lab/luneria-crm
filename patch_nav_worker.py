with open('frontend/src/app/dashboard/layout.tsx', 'r') as f:
    content = f.read()

import re

# Add Emails to WORKER navigation
if "{ name: 'Почты', href: '/dashboard/emails', icon: Mail }" not in content.split("if (role === 'WORKER')")[1]:
    content = content.replace(
        "{ name: 'Мои аккаунты', href: '/dashboard/my-accounts', icon: Key },",
        "{ name: 'Мои аккаунты (TG)', href: '/dashboard/my-accounts', icon: Key },\n        { name: 'Почты', href: '/dashboard/emails', icon: Mail },"
    )
    with open('frontend/src/app/dashboard/layout.tsx', 'w') as f:
        f.write(content)
    print("Patched layout for worker")
else:
    print("Already patched")
