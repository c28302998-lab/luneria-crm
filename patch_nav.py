with open('frontend/src/app/dashboard/layout.tsx', 'r') as f:
    content = f.read()

import re

# Add Mail icon to imports
if 'Mail,' not in content and 'Mail }' not in content:
    content = content.replace('MessageSquare,', 'MessageSquare, Mail,')

if "{ name: 'Почты', href: '/dashboard/emails', icon: Mail }" not in content:
    content = content.replace(
        "{ name: 'Telegram', href: '/dashboard/telegram', icon: MessageCircle },",
        "{ name: 'Telegram', href: '/dashboard/telegram', icon: MessageCircle },\n    { name: 'Почты', href: '/dashboard/emails', icon: Mail },"
    )
    with open('frontend/src/app/dashboard/layout.tsx', 'w') as f:
        f.write(content)
    print("Patched layout.tsx")
else:
    print("Already patched")
