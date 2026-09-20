files = ["src/app/dashboard/telegram-accounts/page.tsx", "src/app/dashboard/telegram/page.tsx"]
for filename in files:
    with open(filename, "r") as f:
        content = f.read()
    
    content = content.replace("import { parsePhoneNumberFromString } from 'libphonenumber-js';\n'use client';", "'use client';\nimport { parsePhoneNumberFromString } from 'libphonenumber-js';")
    
    with open(filename, "w") as f:
        f.write(content)
